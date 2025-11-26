import logging
import json
import os
import sqlite3
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
    function_tool,
    RunContext
)

# murf may be provided as a local/custom plugin in some environments.
# Try importing it first and fall back gracefully if it's not installed.
try:
    from livekit.plugins import murf
except Exception:
    murf = None

from livekit.plugins import silero, google, deepgram
try:
    from livekit.plugins import noise_cancellation
except Exception:
    noise_cancellation = None

logger = logging.getLogger("fraud_agent")

load_dotenv(".env.local")

# Database path
FRAUD_DB_PATH = "fraud_cases.db"


def get_db_connection():
    """Get a connection to the fraud cases database."""
    return sqlite3.connect(FRAUD_DB_PATH)


class FraudAlertAssistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a professional Fraud Detection Representative for SecureBank, a leading financial institution committed to protecting customers from fraudulent transactions.

**Your Personality:**
- Calm, professional, and reassuring
- Clear and direct in communication
- Empathetic to customer concerns
- Security-conscious but not alarming
- Trustworthy and authoritative

**Your Role:**
You are contacting customers about suspicious transactions detected on their accounts. Your goal is to verify the legitimacy of these transactions through a safe verification process and update the case status accordingly.

**Conversation Flow:**

1. **Introduction (immediately)**:
   - Introduce yourself as calling from SecureBank's Fraud Detection Department
   - Explain you're calling about a potentially suspicious transaction
   - Keep the tone professional but reassuring

2. **Request Username**:
   - Ask the customer for their registered username to pull up their case
   - Use the load_fraud_case tool with the provided username
   - If no case is found, politely inform them and end the call

3. **Security Verification**:
   - Ask the security question from the loaded case
   - Wait for their answer
   - Use verify_customer tool to check if the answer matches
   - If verification fails: Politely end the call and mark case as verification_failed
   - If verification succeeds: Proceed to transaction details

4. **Transaction Details**:
   - Read out the suspicious transaction details clearly:
     * Merchant/store name
     * Transaction amount (in Rupees)
     * Date and time of transaction
     * General location
     * Last 4 digits of card used
   - Be specific but professional

5. **Customer Confirmation**:
   - Ask directly: "Did you make this transaction?"
   - Wait for a clear yes or no response
   - If they say YES: The transaction is legitimate
   - If they say NO: The transaction is fraudulent

6. **Case Resolution**:
   - Use update_fraud_case tool to mark the case as:
     * "confirmed_safe" if customer confirms they made the transaction
     * "confirmed_fraud" if customer denies making the transaction
   - Explain next steps:
     * If safe: Thank them and explain it was a routine security check
     * If fraud: Inform them the card will be blocked and they'll receive a new one, a dispute will be filed

7. **Closing**:
   - Thank them for their time and cooperation
   - Remind them to contact the bank immediately if they spot any other suspicious activity
   - End the call professionally

**Important Guidelines:**
- NEVER ask for full card numbers, PINs, passwords, or sensitive credentials
- Only use the security question from the database for verification
- Keep responses concise and voice-friendly (2-3 sentences max)
- If the customer seems confused, reassure them this is a standard security procedure
- Speak clearly and at a moderate pace
- Use the tools provided - don't make up information
- Always update the case status before ending the call
- Be empathetic if customer reports fraud - acknowledge the inconvenience

**Critical Security Notes:**
- All data is demo/sandbox only - this is a simulated fraud alert system
- Never request real sensitive information
- This is for demonstration purposes only

Remember: You're helping protect the customer's account. Be professional, clear, and reassuring throughout the entire conversation!""",
        )

    @function_tool
    async def load_fraud_case(
        self,
        context: RunContext,
        username: str,
    ):
        """Load a fraud case from the database using the customer's username.
        
        Call this tool immediately after the customer provides their username to pull up their case details.
        
        Args:
            username: The customer's registered username (e.g., "John Smith", "Sarah Johnson")
        
        Returns:
            A string containing the fraud case details including security question, transaction info, and card details.
        """
        logger.info(f"Loading fraud case for username: {username}")
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Query for pending cases matching the username (case-insensitive)
            cursor.execute('''
                SELECT id, userName, securityQuestion, securityAnswer, cardEnding,
                       transactionAmount, transactionName, transactionTime, 
                       transactionLocation, transactionCategory
                FROM fraud_cases 
                WHERE LOWER(userName) = LOWER(?) AND caseStatus = 'pending_review'
                LIMIT 1
            ''', (username,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                logger.warning(f"No pending fraud case found for username: {username}")
                return f"No pending fraud case found for username '{username}'. This may be a wrong number. Please verify the customer's identity."
            
            # Store case details in context for later use
            case_data = {
                'case_id': row[0],
                'username': row[1],
                'security_question': row[2],
                'security_answer': row[3],
                'card_ending': row[4],
                'amount': row[5],
                'merchant': row[6],
                'time': row[7],
                'location': row[8],
                'category': row[9]
            }
            
            # Store in agent instance
            self._fraud_case = case_data
            
            result = f"""Fraud case loaded for {case_data['username']}:
- Security Question: {case_data['security_question']}
- Card Ending: {case_data['card_ending']}
- Transaction: ₹{case_data['amount']:.2f} at {case_data['merchant']}
- Date/Time: {case_data['time']}
- Location: {case_data['location']}
- Category: {case_data['category']}

Now proceed with security verification by asking the customer the security question."""
            
            logger.info(f"Successfully loaded case {case_data['case_id']} for {username}")
            return result
            
        except Exception as e:
            logger.error(f"Error loading fraud case: {e}")
            return f"Error loading fraud case: {str(e)}. Please try again."

    @function_tool
    async def verify_customer(
        self,
        context: RunContext,
        customer_answer: str,
    ):
        """Verify the customer's identity by checking their answer to the security question.
        
        Call this tool after the customer answers the security question to verify their identity.
        
        Args:
            customer_answer: The answer provided by the customer to the security question
        
        Returns:
            A verification result indicating if the customer is verified or not.
        """
        logger.info(f"Verifying customer answer: {customer_answer}")
        
        # Get stored case data
        case_data = getattr(self, '_fraud_case', None)
        if not case_data:
            return "Error: No fraud case loaded. Please load the case first using the username."
        
        # Compare answers (case-insensitive)
        correct_answer = case_data['security_answer'].lower().strip()
        provided_answer = customer_answer.lower().strip()
        
        if provided_answer == correct_answer:
            logger.info("Customer verification SUCCESSFUL")
            self._customer_verified = True
            return f"✓ Verification successful! Customer identity confirmed. Now proceed to read out the transaction details and ask if they made this transaction."
        else:
            logger.warning(f"Customer verification FAILED - Expected: {correct_answer}, Got: {provided_answer}")
            self._customer_verified = False
            
            # Mark case as verification failed
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE fraud_cases 
                    SET caseStatus = 'verification_failed',
                        outcomeNote = 'Customer failed security verification',
                        updatedAt = ?
                    WHERE id = ?
                ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), case_data['case_id']))
                conn.commit()
                conn.close()
                logger.info(f"Case {case_data['case_id']} marked as verification_failed")
            except Exception as e:
                logger.error(f"Error updating case status: {e}")
            
            return "✗ Verification failed. The answer provided does not match our records. For security reasons, we cannot proceed with this call. Please contact the bank directly at our official number. Goodbye."

    @function_tool
    async def update_fraud_case(
        self,
        context: RunContext,
        customer_made_transaction: bool,
    ):
        """Update the fraud case status based on the customer's confirmation.
        
        Call this tool after asking if the customer made the transaction and receiving their yes/no answer.
        
        Args:
            customer_made_transaction: True if customer confirms they made the transaction (legitimate), False if they deny it (fraud)
        
        Returns:
            A confirmation message about the case update and next steps.
        """
        logger.info(f"Updating fraud case - Customer made transaction: {customer_made_transaction}")
        
        # Get stored case data
        case_data = getattr(self, '_fraud_case', None)
        if not case_data:
            return "Error: No fraud case loaded. Cannot update status."
        
        # Check if customer was verified
        if not getattr(self, '_customer_verified', False):
            return "Error: Customer identity not verified. Cannot update case status."
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if customer_made_transaction:
                # Transaction is legitimate - mark as safe
                new_status = 'confirmed_safe'
                outcome_note = f"Customer {case_data['username']} confirmed the transaction to {case_data['merchant']} for ₹{case_data['amount']:.2f} as legitimate."
                
                cursor.execute('''
                    UPDATE fraud_cases 
                    SET caseStatus = ?,
                        outcomeNote = ?,
                        updatedAt = ?
                    WHERE id = ?
                ''', (new_status, outcome_note, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), case_data['case_id']))
                
                conn.commit()
                conn.close()
                
                logger.info(f"Case {case_data['case_id']} marked as {new_status}")
                
                return f"""✓ Case marked as SAFE. Transaction confirmed as legitimate.

Next steps to communicate to customer:
- Thank them for confirming the transaction
- Explain this was a routine security check to protect their account
- Remind them to contact us immediately if they notice any unauthorized transactions
- Thank them for their time and cooperation"""
                
            else:
                # Transaction is fraudulent - mark as fraud
                new_status = 'confirmed_fraud'
                outcome_note = f"Customer {case_data['username']} denied making the transaction to {case_data['merchant']} for ₹{case_data['amount']:.2f}. Fraudulent activity confirmed."
                
                cursor.execute('''
                    UPDATE fraud_cases 
                    SET caseStatus = ?,
                        outcomeNote = ?,
                        updatedAt = ?
                    WHERE id = ?
                ''', (new_status, outcome_note, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), case_data['case_id']))
                
                conn.commit()
                conn.close()
                
                logger.info(f"Case {case_data['case_id']} marked as {new_status}")
                
                return f"""⚠ Case marked as FRAUDULENT. Immediate action required.

Next steps to communicate to customer:
- Acknowledge the fraudulent transaction
- Inform them the card ending in {case_data['card_ending']} will be blocked immediately
- A new card will be issued and sent to their registered address within 5-7 business days
- A dispute has been filed and the amount will be credited back to their account
- They should monitor their account for any other suspicious activity
- Thank them for reporting this and helping us keep their account secure"""
        
        except Exception as e:
            logger.error(f"Error updating fraud case: {e}")
            return f"Error updating case status: {str(e)}"


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Logging setup
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Select TTS implementation: prefer Murf if available, otherwise fall back to Google TTS
    try:
        if murf is not None:
            tts_obj = murf.TTS(
                voice="en-US-matthew",
                style="Conversation",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
                text_pacing=True,
            )
        else:
            try:
                tts_obj = google.TTS(voice="en-US-Standard-J")
            except Exception:
                tts_obj = None
    except Exception:
        tts_obj = None

    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=tts_obj,
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    # Metrics collection
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # Start the session
    assistant = FraudAlertAssistant()
    await session.start(
        agent=assistant,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC() if noise_cancellation else None,
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()
    
    # Initial greeting for fraud alert
    await session.say(
        "Hello, this is Agent Martinez from SecureBank's Fraud Detection Department. "
        "We've detected a potentially suspicious transaction on your account and I'm calling to verify its legitimacy. "
        "May I please have your registered username to pull up your case?",
        allow_interruptions=True
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))




