<?php
session_start();

// Database connection details
$servername = "mariadb";
$username = "root"; // Consider using a less privileged user in production
$password = "mht85";
$dbname = "Banco";    // Use the DB name defined in docker-compose for initial creation

// Error reporting for mysqli
mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);

$conn = null; // Initialize connection variable
$login_error = ""; // Initialize error message
// Keep track of plain DNI if form was submitted
$plain_dni_from_form = isset($_POST["dni"]) ? $_POST["dni"] : '';


try {
    // Create connection
    $conn = new mysqli($servername, $username, $password, $dbname);

    if ($_SERVER["REQUEST_METHOD"] == "POST") {
        // $plain_dni_from_form is already set above
        $password_from_form = $_POST["password"]; // Corrected variable name

        // Hash the DNI from the form
        $hashed_dni_from_form = hash('sha256', $plain_dni_from_form);

        // Hash the Password from the form
        $hashed_password_from_form = hash('sha256', $password_from_form);

        // Query using the HASHED DNI
        $sql = "SELECT * FROM Usuarios WHERE dni_usuario = ?";
        $stmt = $conn->prepare($sql);

        if ($stmt) {
            // Bind the HASHED DNI
            $stmt->bind_param("s", $hashed_dni_from_form);
            $stmt->execute();
            $result = $stmt->get_result();

            if ($result->num_rows > 0) {
                $user = $result->fetch_assoc();

                // Compare HASHED passwords
                if ($hashed_password_from_form === $user['contraseña']) {
                    // Password matches
                    $_SESSION["loggedin"] = true;
                    $_SESSION["dni_usuario_plain"] = $plain_dni_from_form; // Store plain DNI

                    $stmt->close();
                    $conn->close();
                    // --- UPDATE REDIRECT LOCATION ---
                    header("Location: ../banco.php"); // Redirect to banco.php
                    exit();
                } else {
                    $login_error = "Invalid password.";
                }
            } else {
                $login_error = "No user found with that DNI.";
            }
            $stmt->close();
        } else {
            $login_error = "Database query preparation error.";
        }
    }

} catch (mysqli_sql_exception $e) {
    $login_error = "Database Error: " . $e->getMessage();
    // error_log("Database Error: " . $e->getMessage());
    // $login_error = "An error occurred during login.";
} finally {
    if ($conn instanceof mysqli && $conn->thread_id) {
        $conn->close();
    }
}

// --- HTML Output Section --- Only runs if not redirected
?>
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
</head>
<body>
    <h2>Login</h2>
    <form action="login.php" method="post">
        <label for="dni">DNI:</label><br>
        <input type="text" id="dni" name="dni" required value="<?php echo htmlspecialchars($plain_dni_from_form); ?>"><br><br>
        <label for="password">Password:</label><br>
        <input type="password" id="password" name="password" required><br><br> <!-- Corrected input name -->
        <input type="submit" value="Login">
    </form>
    <p id="error-message" style="color: red;">
        <?php echo htmlspecialchars($login_error); ?>
    </p>

    <p>Don't have an account? <a href="../registro.html">Register here</a></p>
</body>
</html>