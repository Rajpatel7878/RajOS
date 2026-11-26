package com.rajos.android.firebase

import android.app.NotificationChannel
import android.app.NotificationManager
import android.os.Build
import android.util.Log
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage
import com.rajos.android.R
import com.rajos.android.network.FcmTokenRegistrar

class MyFirebaseMessagingService : FirebaseMessagingService() {

    private val channelId = "rajos_reminders"
    private val channelName = "RajOS Reminders"
    private val channelDesc = "RajOS personal assistant reminders"

    override fun onNewToken(token: String) {
        super.onNewToken(token)
        Log.d(TAG, "Refreshed token: $token")
        // Keep the backend in sync whenever Firebase rotates the token
        FcmTokenRegistrar.register(this, token)
    }

    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        Log.d(TAG, "Received message: ${remoteMessage.data}")

        // Handle data payload
        if (remoteMessage.data.isNotEmpty()) {
            Log.d(TAG, "Message data payload: ${remoteMessage.data}")
        }

        // Check for notification payload
        remoteMessage.notification?.let { notification ->
            Log.d(TAG, "Message Notification Body: ${notification.body}")
        }

        // Show notification if app is in foreground/background
        showNotification(remoteMessage.data)
    }

    /**
     * Show a notification from received FCM data
     */
    private fun showNotification(data: Map<String, String>) {
        // Create notification channel (required for Android O+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId,
                channelName,
                NotificationManager.IMPORTANCE_DEFAULT
            ).apply {
                description = channelDesc
            }
            val manager = getSystemService(NotificationManager::class.java)
            manager?.createNotificationChannel(channel)
        }

        // Build notification
        val notification = NotificationCompat.Builder(this, channelId)
            .setSmallIcon(R.drawable.ic_launcher_foreground)
            .setContentTitle("RajOS Reminder")
            .setContentText(data["title"] ?: "You have a pending reminder")
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setCategory(NotificationCompat.CATEGORY_REMINDER)
            .setAutoCancel(true)
            .build()

        // Show the notification
        NotificationManagerCompat.from(this).notify(1, notification)
    }

    companion object {
        private const val TAG = "FCM"
    }
}
