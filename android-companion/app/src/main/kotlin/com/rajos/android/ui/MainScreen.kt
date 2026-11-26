package com.rajos.android.ui

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.provider.Settings
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat

/** Which form the authentication dialog shows. */
enum class AuthMode { LOGIN, SIGN_UP }

@Composable
fun MainScreen(
    loggedInEmail: String?,
    authDialogVisible: Boolean,
    authMode: AuthMode,
    authInProgress: Boolean,
    authError: String?,
    onLoginClicked: () -> Unit,
    onSignUpClicked: () -> Unit,
    onAuthModeChange: (AuthMode) -> Unit,
    onAuthSubmit: (mode: AuthMode, username: String, email: String, password: String) -> Unit,
    onAuthDismiss: () -> Unit,
    onConnectClicked: () -> Unit,
    onLogoutClicked: () -> Unit
) {
    val context = LocalContext.current

    // Bitmask of granted permissions, see checkAllPermissions()
    val permissionsStatus by remember { mutableIntStateOf(checkAllPermissions(context)) }
    val allPermissionsGranted = permissionsStatus == ALL_PERMISSIONS

    var voiceAnnouncements by remember { mutableStateOf(true) }
    var pushNotifications by remember { mutableStateOf(true) }
    var quietHours by remember { mutableStateOf(false) }

    if (authDialogVisible) {
        AuthDialog(
            mode = authMode,
            inProgress = authInProgress,
            errorMessage = authError,
            onModeChange = onAuthModeChange,
            onDismiss = onAuthDismiss,
            onSubmit = onAuthSubmit
        )
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // App header
        Text(
            text = "RajOS Personal Assistant",
            style = MaterialTheme.typography.headlineSmall
        )

        // Permission status banner
        if (!allPermissionsGranted) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
                colors = CardDefaults.cardColors(containerColor = Color(0xFFFFE6E6))
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = if (permissionsStatus and PERMISSION_NOTIFICATIONS == 0) {
                            "\u26A0\uFE0F Notification permission is required for reminders. Please enable it in settings."
                        } else {
                            "\u26A0\uFE0F Some permissions are required for full functionality. Please enable them in settings."
                        },
                        style = MaterialTheme.typography.bodyMedium
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Button(onClick = { openAppSettings(context) }) {
                        Text("Open Settings")
                    }
                }
            }
        }

        // Connection / account card
        Card(
            modifier = Modifier.fillMaxWidth(),
            elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "Account",
                    style = MaterialTheme.typography.titleMedium
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = loggedInEmail?.let { "Signed in as $it" } ?: "Not signed in",
                    style = MaterialTheme.typography.bodyMedium,
                    color = if (loggedInEmail == null) {
                        MaterialTheme.colorScheme.onSurfaceVariant
                    } else {
                        MaterialTheme.colorScheme.primary
                    }
                )
                Spacer(modifier = Modifier.height(16.dp))

                Button(
                    onClick = onConnectClicked,
                    modifier = Modifier.fillMaxWidth(),
                    enabled = allPermissionsGranted && loggedInEmail != null
                ) {
                    Text("Connect Device")
                }

                if (!allPermissionsGranted) {
                    Text(
                        text = "\u26A0\uFE0F Enable permissions first",
                        style = MaterialTheme.typography.bodySmall,
                        modifier = Modifier.padding(top = 8.dp)
                    )
                }

                Spacer(modifier = Modifier.height(8.dp))

                Button(
                    onClick = onLoginClicked,
                    modifier = Modifier.fillMaxWidth(),
                    enabled = allPermissionsGranted && loggedInEmail == null
                ) {
                    Text("Login")
                }

                Spacer(modifier = Modifier.height(8.dp))

                Button(
                    onClick = onSignUpClicked,
                    modifier = Modifier.fillMaxWidth(),
                    enabled = allPermissionsGranted && loggedInEmail == null
                ) {
                    Text("Create Account")
                }

                Spacer(modifier = Modifier.height(8.dp))

                Button(
                    onClick = onLogoutClicked,
                    modifier = Modifier.fillMaxWidth(),
                    enabled = allPermissionsGranted && loggedInEmail != null
                ) {
                    Text("Logout")
                }
            }
        }

        // Reminders section
        Card(
            modifier = Modifier.fillMaxWidth(),
            elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "Upcoming Reminders",
                    style = MaterialTheme.typography.titleMedium
                )
                Spacer(modifier = Modifier.height(16.dp))

                if (!allPermissionsGranted) {
                    Text(
                        text = "\u26A0\uFE0F Connect a device and enable permissions to see reminders",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.error
                    )
                } else {
                    // TODO: Display active reminders from API
                    Text(
                        text = "No active reminders",
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
            }
        }

        // Settings section
        Card(
            modifier = Modifier.fillMaxWidth(),
            elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "Settings",
                    style = MaterialTheme.typography.titleMedium
                )
                Spacer(modifier = Modifier.height(16.dp))

                SettingRow(
                    title = "Voice Announcements",
                    subtitle = "Spoken reminders and briefings",
                    checked = voiceAnnouncements,
                    enabled = allPermissionsGranted,
                    onCheckedChange = { voiceAnnouncements = it }
                )

                HorizontalDivider(modifier = Modifier.padding(vertical = 8.dp))

                SettingRow(
                    title = "Push Notifications",
                    subtitle = "Remote notifications via Firebase",
                    checked = pushNotifications,
                    enabled = allPermissionsGranted,
                    onCheckedChange = { pushNotifications = it }
                )

                HorizontalDivider(modifier = Modifier.padding(vertical = 8.dp))

                SettingRow(
                    title = "Quiet Hours",
                    subtitle = "Suppress notifications during sleep",
                    checked = quietHours,
                    enabled = allPermissionsGranted,
                    onCheckedChange = { quietHours = it }
                )
            }
        }
    }
}

@Composable
private fun AuthDialog(
    mode: AuthMode,
    inProgress: Boolean,
    errorMessage: String?,
    onModeChange: (AuthMode) -> Unit,
    onDismiss: () -> Unit,
    onSubmit: (mode: AuthMode, username: String, email: String, password: String) -> Unit
) {
    var username by rememberSaveable { mutableStateOf("") }
    var email by rememberSaveable { mutableStateOf("") }
    var password by rememberSaveable { mutableStateOf("") }
    var confirmPassword by rememberSaveable { mutableStateOf("") }

    var usernameError by rememberSaveable { mutableStateOf<String?>(null) }
    var emailError by rememberSaveable { mutableStateOf<String?>(null) }
    var passwordError by rememberSaveable { mutableStateOf<String?>(null) }
    var confirmPasswordError by rememberSaveable { mutableStateOf<String?>(null) }

    val isSignUp = mode == AuthMode.SIGN_UP

    fun validateAndSubmit() {
        usernameError = if (isSignUp) AuthValidation.username(username) else null
        emailError = AuthValidation.email(email)
        passwordError = if (isSignUp) {
            AuthValidation.password(password)
        } else {
            AuthValidation.requiredPassword(password)
        }
        confirmPasswordError = if (isSignUp) {
            AuthValidation.confirmPassword(password, confirmPassword)
        } else {
            null
        }

        if (usernameError == null && emailError == null &&
            passwordError == null && confirmPasswordError == null
        ) {
            onSubmit(mode, username.trim(), email.trim(), password)
        }
    }

    fun clearErrors() {
        usernameError = null
        emailError = null
        passwordError = null
        confirmPasswordError = null
    }

    AlertDialog(
        onDismissRequest = { if (!inProgress) onDismiss() },
        title = { Text(if (isSignUp) "Create your RajOS account" else "Sign in to RajOS") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                if (isSignUp) {
                    OutlinedTextField(
                        value = username,
                        onValueChange = {
                            username = it
                            if (usernameError != null) {
                                usernameError = AuthValidation.username(it)
                            }
                        },
                        label = { Text("Username") },
                        singleLine = true,
                        enabled = !inProgress,
                        isError = usernameError != null,
                        supportingText = {
                            usernameError?.let { Text(it) }
                        },
                        modifier = Modifier.fillMaxWidth()
                    )
                }
                OutlinedTextField(
                    value = email,
                    onValueChange = {
                        email = it
                        if (emailError != null) {
                            emailError = AuthValidation.email(it)
                        }
                    },
                    label = { Text("Email") },
                    singleLine = true,
                    enabled = !inProgress,
                    isError = emailError != null,
                    supportingText = {
                        emailError?.let { Text(it) }
                    },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email),
                    modifier = Modifier.fillMaxWidth()
                )
                OutlinedTextField(
                    value = password,
                    onValueChange = {
                        password = it
                        if (passwordError != null) {
                            passwordError = if (isSignUp) {
                                AuthValidation.password(it)
                            } else {
                                AuthValidation.requiredPassword(it)
                            }
                        }
                    },
                    label = { Text("Password") },
                    singleLine = true,
                    enabled = !inProgress,
                    isError = passwordError != null,
                    supportingText = {
                        if (passwordError != null) {
                            Text(passwordError!!)
                        } else if (isSignUp) {
                            Text(AuthValidation.PASSWORD_HINT)
                        }
                    },
                    visualTransformation = PasswordVisualTransformation(),
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                    modifier = Modifier.fillMaxWidth()
                )
                if (isSignUp) {
                    OutlinedTextField(
                        value = confirmPassword,
                        onValueChange = {
                            confirmPassword = it
                            if (confirmPasswordError != null) {
                                confirmPasswordError =
                                    AuthValidation.confirmPassword(password, it)
                            }
                        },
                        label = { Text("Confirm password") },
                        singleLine = true,
                        enabled = !inProgress,
                        isError = confirmPasswordError != null,
                        supportingText = {
                            confirmPasswordError?.let { Text(it) }
                        },
                        visualTransformation = PasswordVisualTransformation(),
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                        modifier = Modifier.fillMaxWidth()
                    )
                }
                if (errorMessage != null) {
                    Text(
                        text = errorMessage,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.error
                    )
                }
                TextButton(
                    onClick = {
                        clearErrors()
                        onModeChange(if (isSignUp) AuthMode.LOGIN else AuthMode.SIGN_UP)
                    },
                    enabled = !inProgress
                ) {
                    Text(
                        if (isSignUp) {
                            "Already have an account? Sign in"
                        } else {
                            "New here? Create an account"
                        }
                    )
                }
            }
        },
        confirmButton = {
            if (inProgress) {
                CircularProgressIndicator(
                    modifier = Modifier
                        .padding(horizontal = 16.dp)
                        .size(24.dp),
                    strokeWidth = 2.dp
                )
            } else {
                TextButton(onClick = { validateAndSubmit() }) {
                    Text(if (isSignUp) "Create account" else "Sign in")
                }
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss, enabled = !inProgress) {
                Text("Cancel")
            }
        }
    )
}

@Composable
private fun SettingRow(
    title: String,
    subtitle: String,
    checked: Boolean,
    enabled: Boolean,
    onCheckedChange: (Boolean) -> Unit
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Text(text = title, style = MaterialTheme.typography.bodyLarge)
            Text(
                text = subtitle,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
        Spacer(modifier = Modifier.width(8.dp))
        Switch(
            checked = checked,
            onCheckedChange = onCheckedChange,
            enabled = enabled
        )
    }
}

private fun openAppSettings(context: Context) {
    val intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
        data = Uri.fromParts("package", context.packageName, null)
        addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
    }
    context.startActivity(intent)
}

private const val PERMISSION_FOREGROUND_SERVICE = 1
private const val PERMISSION_NOTIFICATIONS = 2
private const val PERMISSION_SET_ALARM = 4
private const val ALL_PERMISSIONS =
    PERMISSION_FOREGROUND_SERVICE or PERMISSION_NOTIFICATIONS or PERMISSION_SET_ALARM

/**
 * Check all critical permissions and return a bitmask:
 * Bit 0 (1): Foreground service permission
 * Bit 1 (2): Notification permission (POST_NOTIFICATIONS)
 * Bit 2 (4): Set alarm permission
 */
private fun checkAllPermissions(context: Context): Int {
    var result = 0

    if (ContextCompat.checkSelfPermission(context, Manifest.permission.FOREGROUND_SERVICE)
        == PackageManager.PERMISSION_GRANTED
    ) {
        result = result or PERMISSION_FOREGROUND_SERVICE
    }

    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        if (ContextCompat.checkSelfPermission(context, Manifest.permission.POST_NOTIFICATIONS)
            == PackageManager.PERMISSION_GRANTED
        ) {
            result = result or PERMISSION_NOTIFICATIONS
        }
    } else {
        // On older Android versions notifications are enabled by default
        result = result or PERMISSION_NOTIFICATIONS
    }

    if (ContextCompat.checkSelfPermission(context, Manifest.permission.SET_ALARM)
        == PackageManager.PERMISSION_GRANTED
    ) {
        result = result or PERMISSION_SET_ALARM
    }

    return result
}
