<?php
    session_start(); // Start the session at the very beginning
?>
<!DOCTYPE html>
<html>
<head>
    <title>Banco Main Menu</title>
</head>
<body>
    <h2>Welcome to Banco!</h2>

    <?php
        // Check if the user is logged in by looking at the session variable
        if (isset($_SESSION["loggedin"]) && $_SESSION["loggedin"] === true) {
            // User is logged in
            echo "<h3>Your Account Info:</h3>";
            // Display user info stored in the session
            // Use htmlspecialchars to prevent XSS issues when displaying user data
            if (isset($_SESSION["dni_usuario_plain"])) {
                 echo "<p>DNI: " . htmlspecialchars($_SESSION["dni_usuario_plain"]) . "</p>";
            } else {
                 echo "<p>DNI: Not available</p>"; // Fallback if plain DNI wasn't stored
            }
            // Add placeholders for other potential info or actions
            echo "<p><i>More account details or actions can be added here.</i></p>";

            // Provide a logout link, pointing to the correct logout script path
            echo "<p><a href='php/logout.php'>Logout</a></p>";

        } else {
            // User is not logged in, show login/register links
            echo "<p>Please log in or register to access your account.</p>";
            echo "<p><a href='login.html'>Login</a></p>"; // Link to your login form page
            echo "<p><a href='registro.html'>Register</a></p>"; // Link to your registration page
        }
    ?>

</body>
</html>