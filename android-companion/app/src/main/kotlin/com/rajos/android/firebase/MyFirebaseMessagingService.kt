package com.rajos.android.firebase

import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage
import com.rajos.android.R

class MyFirebaseMessagingService : FirebaseMessagingService() {

    private val CHANNEL_ID = "rajos_reminders"
    private val CHANNEL_NAME = "RajOS Reminders"
    private val CHANNEL_DESC = "RajOS personal assistant reminders"

    override fun onNewToken(token: String) {
        super.onNewToken(token)
        Log.d("FCM", "Refreshed token: $token")
        // TODO: Register this token with your backend via your API
        // Example: API.registerFCMToken(token)
    }

    override fun onMessageReceived remoteMessage: RemoteMessage {
        Log.d("FCM", "Received message: ${remoteMessage.data}")

        // Handle data payload
        if (remoteMessage.data.isNotEmpty()) {
            Log.d("FCM", "Message data payload: ${remoteMessage.data}")
        }

        // Check for notification payload
        remoteMessage.notification?.let { notification ->
            Log.d("FCM", "Message Notification Body: ${notification.body}")
        }

        // Show notification if app is in foreground/background
        showNotification(remoteMessage.data)
    }

    override fun onMessageSent(messageId: Int) {
        super.onMessageSent(messageId)
        Log.d("FCM", "Message sent: $messageId")
    }

    override fun onSendFailed(errorCode: Int) {
        super.onSendFailed(errorCode)
        Log.e("FCM", "Message send failed: $errorCode")
    }

    /**
     * Show a notification from received FCM data
     */
    private fun showNotification(data: Map<String, String>) {
        // Create notification channel (required for Android O+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                CHANNEL_NAME,
                NotificationManager.IMPORTANCE_DEFAULT
            ).apply {
                description = CHANNEL_DESC
            }
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }

        // Build notification
        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_launcher_foreground)
            .setContentTitle("RajOS Reminder")
            .setContentText(data.getOrDefault("title", "You have a pending reminder"))
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setCategory(NotificationCompat.CATEGORY_REMINDER)
            .setAutoCancel(true)
            .build()

        // Show the notification
        NotificationManagerCompat.from(this).notify(1, notification)
    }
}