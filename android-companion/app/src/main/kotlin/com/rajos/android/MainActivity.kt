package com.rajos.android

import android.Manifest
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.util.Log
import androidx.activity.compose.setContent
import androidx.appcompat.app.AppCompatActivity
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.google.firebase.FirebaseApp
import com.google.firebase.messaging.FirebaseMessaging
import com.rajos.android.network.AuthRepository
import com.rajos.android.network.FcmTokenRegistrar
import com.rajos.android.ui.AuthMode
import com.rajos.android.ui.MainScreen
import com.rajos.android.ui.theme.RajOSTheme

class MainActivity : AppCompatActivity() {

    private var permissionsGranted = false

    private lateinit var authRepository: AuthRepository

    // Compose-observable authentication state
    private var loggedInEmail by mutableStateOf<String?>(null)
    private var authDialogVisible by mutableStateOf(false)
    private var authMode by mutableStateOf(AuthMode.LOGIN)
    private var authInProgress by mutableStateOf(false)
    private var authError by mutableStateOf<String?>(null)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        authRepository = AuthRepository(this)

        // A rejected or expired JWT drops the session and asks the user to sign in again.
        AuthRepository.onSessionExpired = {
            loggedInEmail = null
            authMode = AuthMode.LOGIN
            authError = "Your session expired. Please sign in again."
            authDialogVisible = true
        }

        // Request critical permissions before initializing
        requestPermissions()

        if (FirebaseApp.getApps(this).isEmpty()) {
            Log.w("FCM", "Firebase is not configured (app/google-services.json missing); skipping FCM token retrieval")
        }

        // Restore the saved session, silently renewing the access token with the
        // refresh token when it has expired.
        authRepository.restoreSession { email ->
            loggedInEmail = email
            if (email != null && FirebaseApp.getApps(this).isNotEmpty()) {
                registerFcmToken()
            }
        }

        // Request permission to post notifications (Android 13+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS)
                != PackageManager.PERMISSION_GRANTED
            ) {
                ActivityCompat.requestPermissions(
                    this,
                    arrayOf(Manifest.permission.POST_NOTIFICATIONS),
                    1001
                )
            }
        }

        // Set up the Jetpack Compose UI
        setContent {
            RajOSTheme {
                MainScreen(
                    loggedInEmail = loggedInEmail,
                    authDialogVisible = authDialogVisible,
                    authMode = authMode,
                    authInProgress = authInProgress,
                    authError = authError,
                    onLoginClicked = { openAuthDialog(AuthMode.LOGIN) },
                    onSignUpClicked = { openAuthDialog(AuthMode.SIGN_UP) },
                    onAuthModeChange = { mode ->
                        authMode = mode
                        authError = null
                    },
                    onAuthSubmit = { mode, username, email, password ->
                        performAuth(mode, username, email, password)
                    },
                    onAuthDismiss = {
                        if (!authInProgress) {
                            authDialogVisible = false
                            authError = null
                        }
                    },
                    onConnectClicked = { handleConnect() },
                    onLogoutClicked = { handleLogout() }
                )
            }
        }
    }

    override fun onDestroy() {
        AuthRepository.onSessionExpired = null
        super.onDestroy()
    }

    private fun openAuthDialog(mode: AuthMode) {
        authMode = mode
        authError = null
        authDialogVisible = true
    }

    /** Fetch the current FCM token and hand it to the backend, now with the user's JWT. */
    private fun registerFcmToken() {
        FirebaseMessaging.getInstance().token.addOnCompleteListener { task ->
            if (task.isSuccessful) {
                val token = task.result
                Log.d("FCM", "FCM Token: $token")
                FcmTokenRegistrar.register(this, token)
            } else {
                Log.d("FCM", "FCM token retrieval failed")
            }
        }
    }

    private fun performAuth(mode: AuthMode, username: String, email: String, password: String) {
        if (email.isBlank() || password.isBlank()) {
            authError = "Email and password are required"
            return
        }
        if (mode == AuthMode.SIGN_UP && username.isBlank()) {
            authError = "Username is required"
            return
        }

        authInProgress = true
        authError = null

        val onResult: (Result<String>) -> Unit = { result ->
            authInProgress = false
            result.onSuccess { signedInEmail ->
                loggedInEmail = signedInEmail
                authDialogVisible = false
                // Re-send the FCM token so the backend attaches it to this user
                if (FirebaseApp.getApps(this).isNotEmpty()) {
                    registerFcmToken()
                }
            }.onFailure { error ->
                authError = error.message ?: "Authentication failed"
            }
        }

        when (mode) {
            AuthMode.LOGIN -> authRepository.login(email.trim(), password, onResult)
            AuthMode.SIGN_UP -> authRepository.register(username.trim(), email.trim(), password, onResult)
        }
    }

    private fun requestPermissions() {
        // Request foreground service permission for reminders
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.FOREGROUND_SERVICE)
            != PackageManager.PERMISSION_GRANTED
        ) {
            ActivityCompat.requestPermissions(
                this,
                arrayOf(Manifest.permission.FOREGROUND_SERVICE),
                1000
            )
        }

        // Request SET_ALARM permission for scheduled reminders
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.SET_ALARM)
            != PackageManager.PERMISSION_GRANTED
        ) {
            ActivityCompat.requestPermissions(
                this,
                arrayOf(Manifest.permission.SET_ALARM),
                1002
            )
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
                    permissionsGranted = true
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

    private fun handleConnect() {
        // TODO: Implement device connection flow
        Log.d("MainActivity", "Connect device clicked")
    }

    private fun handleLogout() {
        authRepository.logout()
        loggedInEmail = null
        Log.d("MainActivity", "Signed out")
    }
}
