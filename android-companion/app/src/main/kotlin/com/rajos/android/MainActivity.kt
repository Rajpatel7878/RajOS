package com.rajos.android

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.util.Log
import androidx.appcompat.app.AppCompatActivity
import androidx.compose.ui.platform.setContentView
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.rajos.android.ui.theme.RajOSTheme
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.launch
import com.google.firebase.messaging.FirebaseMessaging

class MainActivity : AppCompatActivity() {

    private lateinit var viewModel: MainViewModel
    private var permissionsGranted = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Request critical permissions before initializing
        requestPermissions()

        // Initialize Firebase Cloud Messaging for push notifications
        FirebaseMessaging.getInstance().token.addOnCompleteListener { task ->
            if (task.isSuccessful) {
                val token = task.result
                Log.d("FCM", "FCM Token: $token")
                // TODO: Register token with backend via API
            } else {
                Log.d("FCM", "FCM token retrieval failed")
            }
        }

        // Request permission to post notifications (Android 13+)
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) 
                != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this,
                    arrayOf(Manifest.permission.POST_NOTIFICATIONS), 1001)
            }
        }

        // Set up the Jetpack Compose UI
        setContentView(RajOSTheme {
            MainScreen(
                onLoginClicked = { handleLogin() },
                onConnectClicked = { handleConnect() },
                onLogoutClicked = { handleLogout() }
            )
        })
    }

    private fun requestPermissions() {
        // Request foreground service permission for reminders
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.FOREGROUND_SERVICE) 
            != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this,
                arrayOf(Manifest.permission.FOREGROUND_SERVICE), 1000)
        }

        // Request SET_ALARM permission for scheduled reminders
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.SET_ALARM) 
            != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this,
                arrayOf(Manifest.permission.SET_ALARM), 1002)
        }
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        when (requestCode) {
            1000 -> {
                // Foreground service permission
                if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                    Log.d("Permissions", "Foreground service permission granted")
                }
            }
            1001 -> {
                // Notification permission
                if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                    Log.d("Permissions", "Notification permission granted")
                }
            }
            1002 -> {
                // Set alarm permission
                if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                    Log.d("Permissions", "Set alarm permission granted")
                }
            }
        }
    }

    private fun handleLogin() {
        // TODO: Implement login flow
        Log.d("MainActivity", "Login clicked")
    }

    private fun handleConnect() {
        // TODO: Implement device connection flow
        Log.d("MainActivity", "Connect device clicked")
    }

    private fun handleLogout() {
        // TODO: Implement logout flow
        Log.d("MainActivity", "Logout clicked")
    }
}