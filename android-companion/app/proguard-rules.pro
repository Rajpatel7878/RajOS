# Project specific ProGuard rules.

# Keep Firebase messaging classes used reflectively.
-keep class com.google.firebase.** { *; }
-dontwarn com.google.firebase.**
