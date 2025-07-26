<?php
session_start();
require "inc/tools.php";

$lang = substr($_SERVER['HTTP_ACCEPT_LANGUAGE'], 0, 2);
$lang == "fr" ? $lang = "fr" : $lang = "en";

$_SESSION['lang'] = $lang;

if (isset($_SESSION['banned'])) {
     header('Location: /');
    exit;
}

if (!isset($_SESSION['submited'])) {
    $_SESSION['submited'] = 0;
}

$hide = 'hide';
$error = false;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $_SESSION['submited']++;
    if ($_SESSION['submited'] >= 5) {
        $_SESSION['banned'] = $_SERVER['REMOTE_ADDR'];
        header('Location: /');
        exit;
    }
    if (isset($_POST['first']) && isset($_POST['password'])) {
        if (verifyField($_POST['first']) || verifyField($_POST['password'])) {
            $error = true;
        } elseif ($_POST['first'] === $WEBADMIN[0]  && $_POST['password'] === $WEBADMIN[1]) {
            $_SESSION['auth'] = true;
            header('Location: /admin/');
            exit;
        } else {
            $error = true;
        }
    } else {
        $error = true;
    }
}
function verifyField($value)
{
    global $lang;
    $value = trim($value);
    if (empty($value)) {
        return $lang == "fr" ? "Le champ ne doit pas être vide." : "The field cannot be empty.";
    }
    if (preg_match('/<script>|<\/script>|[<>]/i', $value)) {
        return 'Le champ contient des caractères interdits.';
    }
    return null;
}
if ($_SERVER['REQUEST_METHOD'] === 'POST' && $error) {
    $alertClass = "alert";
    $errorMsg = $lang == "fr" ?  "Identifiant ou mot de passe incorrect." : "Incorrect User name or password.";
}
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    $error = false;
    $errorMsg = "";
}
if (($_SESSION['submited'] > 0  && $error) && (isset($_POST['first']) || isset($_POST['password']))) {
    $hide = 'loginError';
}
?>
<!DOCTYPE html>
<html lang="<?php echo $lang?>">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dj.zic - MC Administration</title>
    <link rel="stylesheet" href="/css/admin.min.css">
</head>

<body class="noBg">

    <div id="modal" class="modal">
        <div class="modal-content">
            <div class="logo login"><a href="/"><?php include '../img/logo.svg'; ?></a></div>
            <h1 class="login">DJ MC Admin</h1>
            <div class="<?php echo $hide ?>">
                <img src="/img/alert.svg" alt="alert"><span>
                    <?php 
                    if ($_SESSION['submited'] < 4 ) {
                         echo $errorMsg;
                    } else {
                        echo $lang == "fr" ? "Avant dernier essais avant bannissement!" : "Penultimate attempt before banishment!";   
                    }?></span>
            </div>
            <form method="post" id="loginForm" action="">
                <div class="wrapper">
                <label for="first"><?php echo $lang == "fr" ? "Identifiant" : "User name"; ?>:</label>
                <input type="text" id="first" name="first" required></div>
                <div class="wrapper"><label for="password"><?php echo $lang == "fr" ? "Mot de Passe" : "Password"; ?>:</label>
                <input type="password" id="password" name="password" required></div>
                <div class="buttons login"><button type="submit" class="action-button login">Ok</button></div>
            </form>
        </div>
    </div>
    <?php 
    $_GET['from'] = 'admin';
    include_once __DIR__ . '/../landscape.php'; 
    
    ?>
</body>

</html>