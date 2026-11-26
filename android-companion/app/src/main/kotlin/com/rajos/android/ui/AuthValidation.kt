package com.rajos.android.ui

import android.util.Patterns

/**
 * Client-side validation for the sign-in / sign-up form.
 * Each function returns an error message, or null when the value is valid.
 */
object AuthValidation {

    const val MIN_PASSWORD_LENGTH = 8
    const val MIN_USERNAME_LENGTH = 3

    const val PASSWORD_HINT =
        "At least $MIN_PASSWORD_LENGTH characters with upper & lower case and a number"

    fun email(email: String): String? {
        val value = email.trim()
        return when {
            value.isEmpty() -> "Email is required"
            !Patterns.EMAIL_ADDRESS.matcher(value).matches() -> "Enter a valid email address"
            else -> null
        }
    }

    /** Sign-up password rules: length plus at least one upper case, lower case and digit. */
    fun password(password: String): String? = when {
        password.isEmpty() -> "Password is required"
        password.length < MIN_PASSWORD_LENGTH ->
            "Password must be at least $MIN_PASSWORD_LENGTH characters"
        !password.any { it.isUpperCase() } -> "Add at least one uppercase letter"
        !password.any { it.isLowerCase() } -> "Add at least one lowercase letter"
        !password.any { it.isDigit() } -> "Add at least one digit"
        else -> null
    }

    /** The confirmation must be non-empty and match the chosen password. */
    fun confirmPassword(password: String, confirmation: String): String? = when {
        confirmation.isEmpty() -> "Please confirm your password"
        confirmation != password -> "Passwords do not match"
        else -> null
    }

    /** Sign-in only checks that a password was entered; older accounts may be shorter. */
    fun requiredPassword(password: String): String? =
        if (password.isEmpty()) "Password is required" else null

    fun username(username: String): String? {
        val value = username.trim()
        return when {
            value.isEmpty() -> "Username is required"
            value.length < MIN_USERNAME_LENGTH ->
                "Username must be at least $MIN_USERNAME_LENGTH characters"
            else -> null
        }
    }
}
