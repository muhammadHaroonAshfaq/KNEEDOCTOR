    def conversational_intake(self, user_message: str):
        """
        Step-by-step conversational patient intake.
        Flow: greet → name → age → problem → pain → plan recommendation
        Returns (response_text, next_step)
        """
        if "intake_step" not in st.session_state:
            st.session_state.intake_step = "greet"
            st.session_state.patient_profile = {}

        step = st.session_state.intake_step
        profile = st.session_state.patient_profile

        # --- Step 1: Greeting ---
        if step == "greet":
            st.session_state.intake_step = "ask_name"
            return "👋 Hi! I'm your KneeDoc AI Coach. What’s your name?", "ask_name"

        # --- Step 2: Ask Name ---
        elif step == "ask_name":
            profile["name"] = user_message.strip().split(" ")[0].capitalize()
            st.session_state.intake_step = "ask_age"
            return f"Nice to meet you, {profile['name']}! 😊 How old are you?", "ask_age"

        # --- Step 3: Ask Age ---
        elif step == "ask_age":
            try:
                age = int("".join([c for c in user_message if c.isdigit()]))
                if 10 < age < 110:
                    profile["age"] = age
                    st.session_state.intake_step = "ask_problem"
                    return (
                        f"Got it, {profile['name']}! What kind of knee problem are you facing — pain, stiffness, or limited movement?",
                        "ask_problem",
                    )
                else:
                    return "Please enter a valid age between 10 and 110.", "ask_age"
            except:
                return "Please tell me your age in numbers (e.g., 45).", "ask_age"

        # --- Step 4: Ask Problem ---
        elif step == "ask_problem":
            profile["problem"] = user_message.strip()
            st.session_state.intake_step = "ask_pain"
            return (
                "Understood. On a scale of 1–10, how severe is your knee pain right now?",
                "ask_pain",
            )

        # --- Step 5: Ask Pain Severity ---
        elif step == "ask_pain":
            try:
                pain = int("".join([c for c in user_message if c.isdigit()]))
                if 0 <= pain <= 10:
                    profile["pain_level"] = pain

                    # Calculate severity 1–4 based on pain intensity
                    severity = 1 if pain <= 3 else 2 if pain <= 6 else 3 if pain <= 8 else 4
                    profile["severity"] = severity

                    # Get exercises based on severity
                    exercises = [
                        ex for ex in getattr(self.loader, "exercises", [])
                        if ex.get("difficulty_level") == severity
                    ]
                    if not exercises:
                        exercises = self.loader.exercises[:3]

                    recs = "\n".join(
                        [f"- {ex['name']}: {ex['primary_benefit']}" for ex in exercises]
                    )
                    st.session_state.intake_step = "recommend"

                    return (
                        f"""Based on your pain level ({pain}/10), your severity is level {severity}.
Here are some recommended exercises for you:
{recs}

Would you like me to guide you step-by-step through these? 💪""",
                        "recommend",
                    )
                else:
                    return "Please give a number between 0 and 10.", "ask_pain"
            except:
                return "Please give your pain level as a number (1–10).", "ask_pain"

        # --- Step 6: Confirm Plan ---
        elif step == "recommend":
            st.session_state.intake_step = "done"
            return (
                "Awesome! Let's begin your guided exercise session. 🏋️ You can ask me for instructions anytime.",
                "done",
            )

        # --- Step 7: Already done ---
        else:
            return (
                f"You're all set, {profile.get('name', 'friend')}! You can now ask for daily routines, safety tips, or progress tracking. ✅",
                "done",
            )
