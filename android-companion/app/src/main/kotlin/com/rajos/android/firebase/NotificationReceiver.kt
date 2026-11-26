package com.rajos.android.firebase

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.os.Build
import android.util.Log
import androidx.core.app.NotificationCompat
import com.rajos.android.MainActivity
import com.rajos.android.R

class NotificationReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        Log.d(TAG, "Received broadcast: ${intent.action}")

        val action = intent.action

        when (action) {
            null, "com.google.firebase.MESSAGING_EVENT" -> {
                // The actual message handling is done by MyFirebaseMessagingService
                Log.d(TAG, "Firebase messaging event received")
            }

            "com.rajos.android.SCHEDULED_REMINDER" -> {
                val reminderId = intent.getStringExtra("reminder_id") ?: "unknown"
                Log.d(TAG, "Scheduled reminder: $reminderId")
                showReminderNotification(context, reminderId)
            }

            else -> {
                Log.d(TAG, "Unknown action: $action")
            }
        }
    }

    private fun showReminderNotification(context: Context, reminderId: String) {
        val notificationIntent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        }

        val pendingIntent = PendingIntent.getActivity(
            context,
            0,
            notificationIntent,
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val manager = context.getSystemService(NotificationManager::class.java)
            manager?.createNotificationChannel(
                NotificationChannel(
                    CHANNEL_ID,
                    "RajOS Reminders",
                    NotificationManager.IMPORTANCE_DEFAULT
                )
            )
        }

        val notification = NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_launcher_foreground)
            .setContentTitle("RajOS Reminder")
            .setContentText("Your reminder is due")
            .setContentIntent(pendingIntent)
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setCategory(NotificationCompat.CATEGORY_REMINDER)
            .setAutoCancel(true)
            .build()

        context.getSystemService(NotificationManager::class.java)
            ?.notify(reminderId.hashCode(), notification)
    }

    companion object {
        private const val TAG = "NotificationReceiver"
        private const val CHANNEL_ID = "rajos_reminders"
    }
}
