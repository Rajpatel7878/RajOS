package com.rajos.android.firebase

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.util.Log
import androidx.core.app.JobIntentService

class NotificationReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        Log.d("NotificationReceiver", "Received broadcast: ${intent.action}")

        // Handle the incoming FCM message or other push events
        val action = intent.action

        when (action) {
            null, "com.google.firebase.MESSAGING_EVENT" -> {
                // Launched via Firebase messaging event intent service
                // The actual message handling is done by MyFirebaseMessagingService
                Log.d("NotificationReceiver", "Firebase messaging event received")
            }

            "com.rajos.android.SCHEDULED_REMINDER" -> {
                // Handle scheduled reminder notification
                val reminderId = intent.getStringExtra("reminder_id") ?: "unknown"
                Log.d("NotificationReceiver", "Scheduled reminder: $reminderId")

                // Create a notification for the scheduled reminder
                val notificationIntent = Intent(context, MainActivity::class.java)
                notificationIntent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK)

                val pendingIntent = PendingIntent.getActivity(
                    context,
                    0,
                    notificationIntent,
                    PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
                )

                val builder = android.app.Notification.Builder(context, "rajos_reminders")
                    .setSmallIcon(R.drawable.ic_launcher_foreground)
                    .setContentTitle("RajOS Reminder")
                    .setContentText("Your reminder is due")
                    .setContentIntent(pendingIntent)
                    .setPriority(android.app.Notification.PRIORITY_DEFAULT)
                    .setAutoCancel(true)

                val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE)
                notificationManager.notify(reminderId.hashCode().toInt(), builder.build())
            }

            else -> {
                Log.d("NotificationReceiver", "Unknown action: $action")
            }
        }
    }
}