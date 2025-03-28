<?php
    session_start();
    // Unset all session variables
    $_SESSION = array();
    // Destroy the session
    session_destroy();
    // --- UPDATE REDIRECT LOCATION ---
    header("Location: ../banco.php"); // Redirect to banco.php after logout
    exit();
?>