# OnePlus + RajOS Jarvis — Phone Setup Guide

This guide walks you through installing RajOS on your OnePlus phone, connecting it to your Windows laptop, and configuring all the features needed for Jarvis to deliver reminders, notifications, voice announcements, and authorized automated phone calls.

---

## 1. Prerequisites

| Item | Description |
|------|-------------|
| **OnePlus phone** | Running OxygenOS 13+ (or Android 13+) |
| **Windows laptop** | Running RajOS backend (Python/FastAPI) |
| **RajOS APK** | Debug APK built from the repository |
| **Internet connection** | Both devices on same Wi-Fi, or laptop with public HTTPS URL (ngrok) |
| **Google account** | For Firebase Cloud Messaging setup |

---

## 2. Install the RajOS APK

### Step 2.1: Enable Unknown Sources
1. On your OnePlus phone, go to **Settings → Security → Install unknown apps**
2. Select **Chrome** (or your file browser) and enable **Allow from this source**
3. If prompted, tap **Allow** to permit installation from the browser

### Step 2.2: Download and Install the APK
1. On your laptop, start the RajOS backend server:
   ```bash
   cd backend && uvicorn app.main:app --reload
   ```
2. The API will be available at `http://127.0.0.1:8000` (or your ngrok URL)
3. Download the debug APK from the CI build artifact or build it locally:
   - From GitHub Actions: download `rajos-android-debug-apk`
   - Or run `./gradlew :app:assembleDebug` locally
4. Transfer the APK file to your OnePlus phone (via USB, email, or cloud storage)
5. Tap the APK file on your phone and select **Install**
6. Tap **Open** when installation completes

---

## 3. Log into RajOS

### Step 3.1: Open the App
1. Launch the **RajOS** app from your app drawer
2. You'll see the login/connect screen

### Step 3.2: Log in or Create Account
1. Tap **Login** 
2. If you already have an account, enter your email/username and password
3. If you're new, tap **Register** and create an account
4. Your account is now linked to your phone

---

## 4. Enable Notification Permissions

### Step 4.1: POST_NOTIFICATIONS Permission (Android 13+)
1. When you first open the app, a system dialog will ask: **"Allow RajOS to post notifications?"**
2. Tap **Allow**
3. If you missed the dialog:
   - Go to **Settings → Apps → RajOS → Notifications → Allow notifications**

### Step 4.2: Foreground Service Permission
1. The app may request permission for **Foreground Service** (needed for scheduled reminders)
2. Tap **Allow**
3. If denied: **Settings → Apps → RajOS → Battery → Disable optimizations → Don't optimize**

### Step 4.3: Set Alarm Permission
1. Required for scheduled reminders to trigger at the right time
2. Tap **Allow** when prompted
3. If denied: **Settings → Apps → RajOS → → Turn on **Set alarm** permission**

---

## 5. Configure Notification Channels

RajOS uses Firebase Cloud Messaging with notification channels for different reminder types.

### Step 5.1: Grant Permissions (First Run Only)
1. Open **Settings → Apps → RajOS → Notifications**
2. Ensure **All notifications** is set to **On**
3. Tap **Notification categories** if available

### Step 5.2: Channel Configuration (Handled by App)
The app creates the following notification channels automatically:
- **`rajos_reminders`** — Default priority for regular reminders
- **`rajos_alerts`** — High priority for overdue/deadline reminders
- **`rajos_briefings`** — Low priority for daily briefings

*On OnePlus/OxygenOS, you can long-press any RajOS notification and tap the gear icon to customize channel settings.*

---

## 6. Allow Background Activity

### Step 6.1: Disable Battery Optimization
1. Go to **Settings → Battery → Battery optimization**
2. Select **All apps** → Find **RajOS** → Change to **Don't optimize**
3. Alternatively: **Settings → Battery → Background usage limits → Allow background activity**

### Step 6.2: Deep Sleep Settings (OnePlus-specific)
1. Go to **Settings → Battery → Battery saver → Auto start**
2. Find **RajOS** and enable **Allow auto start**
3. Enable **Background preferences → Permissions → Allow in background**

### Step 6.3: Do Not Disturb Mode
1. Ensure **Do Not Disturb** is not set to **Total silence** all the time
2. Add **RajOS** to **Exceptions** → Allow notifications, calls, or alarms

---

## 7. Grant Exact Alarm Permission

### Step 7.1: Android 19+ (Exact Alarms)
Starting Android 19, exact alarms require explicit permission.

1. Go to **Settings → Apps → RajOS → Advanced → App permissions → Exact alarms**
2. Tap **Allow**
3. If the option is not visible:
   - On OxygenOS 13+/Android 13+: The system manages this automatically
   - Ensure **Foreground Service** permission is granted (Step 4.1)

### Step 7.2: Verify Alarm Permission
1. Open **Settings → Apps → RajOS → Permissions**
2. Confirm **Exact alarms** shows **Allowed**

---

## 8. Configure Microphone and Speech Permissions (For Voice Announcements)

### Step 8.1: Microphone Permission
1. Go to **Settings → Apps → RajOS → Permissions → Microphone**
2. Select **Allow**
3. This is required for text-to-speech and voice commands

### Step 8.2: Speech Recognition Permission
1. Go to **Settings → Apps → RajOS → Permissions → Speech recognition**
2. Enable **Google Voice Typing** or your preferred engine

### Step 8.3: Test Microphone
1. In the RajOS app, go to **Settings → Voice Announcements**
2. Tap **Test microphone** — should see input level move
3. If no input, check that no other app is using the microphone

---

## 9. Enable Voice Announcements

### Step 9.1: Enable in App
1. Open RajOS app → **Settings → Voice Announcements**
2. Toggle **Spoken reminders and briefings** to **On**

### Step 9.2: Voice Preferences
1. **Speech rate**: Adjust how fast announcements are spoken
2. **Volume**: Set announcement volume (separate from media volume)
3. **Quiet hours**: Set 10 PM–7 AM UTC to suppress non-critical announcements

### Step 9.3: Test a Voice Announcement
1. In the app, go to **Settings → Test voice announcement**
2. You should hear: "This is a test reminder from RajOS"
3. If no sound: Check that your phone is **not** in silent mode

### Step 9.4: Stop Speaking
- During an announcement, tap the **Stop** button that appears
- Or say "Stop speaking" if voice command listening is enabled

---

## 10. Enable Optional Automated Calls (Twilio)

### Step 10.1: Configure Twilio Credentials (Laptop only)
You need to set up Twilio on your laptop (not on the phone):

1. **Create a Twilio account**: https://www.twilio.com/try-console
2. **Get your credentials**:
   - Account SID: From Twilio dashboard
   - Auth Token: From Twilio dashboard  
   - Phone number: Purchase a Twilio number from the console
3. **Set environment variables** in your laptop's terminal (or `.env` file):
   ```bash
   set TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   set TWILIO_AUTH_TOKEN=your_auth_token_here
   set TWILIO_PHONE_NUMBER=+1234567890
   ```
4. **Set BASE_URL** (public HTTPS reachable by Twilio):
   - Install ngrok: `brew install ngrok` or download from ngrok.com
   - Start tunnel: `ngrok http 8000`
   - Use the forwarded URL: `BASE_URL=https://abc123.ngrok.io`
5. **Test the test-call endpoint**:
   ```bash
   curl -X POST http://localhost:8000/auth/phone/test-call \
     -H "Content-Type: application/json" \
     -d '{"phone": "+919876543210", "consent": true}'
   ```

### Step 10.2: Configure in the App
1. Open RajOS app → **Settings → Automated calling**
2. Toggle **Enable test calls** (only appears if Twilio credentials are set)
3. Set **Quiet hours** for calls (10 PM–7 AM UTC by default)
4. Set **Max calls per reminder** and **Daily call limits**

### Step 10.4: Make a Test Call
1. Create a critical reminder in the app
2. If not acknowledged within the escalation interval, the system will:
   - Place an automated call to your +91 number
   - Read the reminder text via text-to-speech
   - Wait for you to say "acknowledge" or "mark completed"
3. The call will stop automatically if the reminder is acknowledged or completed

---

## 11. Setting Quiet Hours

### Step 11.1: In the App
1. RajOS → **Settings → Quiet hours**
2. Default: **10 PM–7 AM UTC**
3. During quiet hours:
   - Push notifications are suppressed (but appear in history)
   - Automated calls are blocked
   - Voice announcements are muted
   - Alarms still fire if explicitly set

### Step 11.2: Override Quiet Hours
- Emergency/critical reminders can bypass quiet hours if marked as critical
- You'll see a banner indicating a reminder was held during quiet hours

---

## 12. Testing a Reminder

### Step 12.1: Create a Test Reminder
1. Open RajOS on your laptop
2. Create a new task/reminder:
   - Title: "Test reminder - snooze me"
   - Set a due date/time (within 15 minutes)
   - Mark as **high priority** if you want a call escalation

### Step 12.2: Verify Notification on Phone
1. Wait for the notification to appear (or pull down shade)
2. Tap the notification → opens RajOS app
3. Tap **Snooze** → reminder rescheduled per your settings
4. Tap **Acknowledge** → escalation stops
5. Tap **Mark Completed** → reminder closed, no further escalation

### Step 12.3: Verify Voice Announcement
- If voice announcements are enabled, the phone should speak the reminder title
- Tap **Stop** to halt the announcement

### Step 12.4: Verify Automated Call (if Twilio configured)
- If the reminder is high-priority and calling is enabled, and it's not during quiet hours:
- The system will place an automated call to your registered +91 number
- Listen and follow the voice instructions
- Say "acknowledge" to stop further escalation

---

## 13. Testing Synchronization

### Step 13.1: Manual Sync
1. On phone: Open RajOS → **Settings → Sync now**
2. On laptop: The app should show "Sync successful"
3. Check that tasks created on laptop appear on phone and vice versa

### Step 13.2: Auto Sync on Boot
- The app registers a BOOT_COMPLETED receiver
- On phone restart, RajOS will automatically sync pending reminders
- First sync may take 10–15 seconds

### Step 13.3: Offline Changes
- Changes made offline on either device are synced on next connection
- Conflict resolution: latest timestamp wins, user can review conflicts

---

## 14. Device Unlinking

### Step 14.1: Unlink from Laptop
1. Open RajOS on phone → **Settings → Device connection → Unlink device**
2. Confirm unlinking
3. The phone will no longer receive notifications from your laptop
4. Your laptop can still create reminders (they just won't reach this phone)

### Step 14.2: Unlink from Account
1. In RajOS web interface: **Settings → Account → Log out from all devices**
2. Or delete your account (permanent, deletes all data)

---

## 15. Troubleshooting Common Issues

| Issue | Solution |
|-------|----------|
| **No notifications** | Check POST_NOTIFICATIONS permission, battery optimization, quiet hours |
| **Calls not placing** | Verify Twilio credentials, not quiet hours, consent given, number format +91 |
| **FCM tokens not registering** | Ensure internet, check Firebase Server Key in .env, restart app |
| **Reminders not triggering** | Check exact alarm permission, set alarm permission, disable battery optimization |
| **Voice not speaking** | Check microphone permission, not silent mode, TTS engine installed |
| **Sync failing** | Both devices on same network, check API URL, restart both devices |
| **APK won't install** | Enable "Unknown sources", minimum API level 24 required |

---

## 16. Quick Reference — Key Settings

| Setting | Location | Default |
|---------|----------|---------|
| Quiet hours | RajOS → Settings → Quiet hours | 10 PM–7 AM UTC |
| Voice announcements | RajOS → Settings → Voice Announcements | Off |
| Push notifications | RajOS → Settings → Push Notifications | On |
| Automated calls | RajOS → Settings → Automated calling | Off (requires Twilio) |
| Exact alarm permission | Android → Apps → RajOS → Permissions → Exact alarms | — |
| Notification channels | Settings → Apps → RajOS → Notifications | 3 channels |

---

## 17. Need Help?

- **Check the main README** for backend setup: `README.md`
- **Review the verification report** for technical details: `docs/RAJOS_TWILIO_FINAL_VERIFICATION.md`
- **GitHub Issues**: Report problems or feature requests
- **OnePlus Community**: OnePlus forums for OxygenOS-specific help

---

**Generated for RajOS V2 — Jarvis Android Companion Integration**
**Do not run Gradle manually. Use GitHub Actions CI workflow for builds.**
**All credentials (Twilio, Firebase) must be kept in `.env`, never committed to git.**