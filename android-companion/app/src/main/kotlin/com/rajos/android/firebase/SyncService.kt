package com.rajos.android.firebase

import android.content.Context
import android.content.Intent
import android.os.PowerManager
import android.util.Log
import androidx.core.app.JobIntentService

class SyncService : JobIntentService() {

    override fun onHandleWork(intent: Intent) {
        Log.d(TAG, "SyncService running")

        // Acquire wake lock to keep CPU running while we sync
        val powerManager = getSystemService(Context.POWER_SERVICE) as PowerManager
        val wakeLock = powerManager.newWakeLock(
            PowerManager.PARTIAL_WAKE_LOCK,
            "RajOS::SyncService::wakeLock"
        )
        wakeLock.acquire(WAKE_LOCK_TIMEOUT_MS)

        try {
            // Sync pending reminders with backend
            syncPendingReminders()

            // Reschedule any pending alarms
            rescheduleAlarms()

            // Update device last seen timestamp
            updateDeviceStatus()
        } finally {
            if (wakeLock.isHeld) {
                wakeLock.release()
            }
        }
    }

    private fun syncPendingReminders() {
        Log.d(TAG, "Syncing pending reminders")

        // TODO: Query database for pending/scheduled reminders
        // TODO: Send them to backend via API
        // TODO: Backend returns delivery status, update local database

        Log.d(TAG, "Pending reminders sync completed")
    }

    private fun rescheduleAlarms() {
        Log.d(TAG, "Rescheduling alarms")

        // TODO: Query persistent scheduler for due reminders
        // TODO: Re-create AlarmManager/PendingIntents for any that are still pending

        Log.d(TAG, "Alarm rescheduling completed")
    }

    private fun updateDeviceStatus() {
        Log.d(TAG, "Updating device status")

        // TODO: Update push subscription last_seen timestamp
        // TODO: Report device online/offline to backend
    }

    companion object {
        const val WORK_ID = 1234
        private const val TAG = "SyncService"
        private const val WAKE_LOCK_TIMEOUT_MS = 10 * 60 * 1000L

        fun enqueueWork(context: Context, intent: Intent) {
            enqueueWork(context, SyncService::class.java, WORK_ID, intent)
        }
    }
}
