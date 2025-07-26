<?php
session_start();

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if (isset($_POST['accept_cgu'])) {

        $_SESSION['accepted_cgu'] = true;
        header('Location: app.php');
        exit();
    }
}
$lang = substr($_SERVER['HTTP_ACCEPT_LANGUAGE'], 0, 2);
$lang == "fr" ? $lang = "fr" : $lang = "en";
$_SESSION['lang'] = $lang;
?>
<!DOCTYPE html>
<html lang="<?php echo $lang ?>">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>dj.zic: Informations d'utilisation.</title>
    <link rel="stylesheet" href="/css/djStyle.min.css">
</head>

<body>

    <div id="modal" class="modal active">
        <div class="modal-content">
            <div class="logo"><a href="/admin/"><?php include 'img/logo.svg'; ?></a></div>

            <?php if ($lang == 'fr') { ?>
                <h1>Streaming musical itinérant gratuit</h1>
                <h2>Internet</h2>
                <p>Ce réseau Wi-Fi n’a pas d’accès au Web.</p>
                <p>Il diffuse en écoute libre le flux audio du DJ sur votre smartphone, sans utiliser votre forfait data..</p>
                <h2>Sécurité</h2>
                <p>Aucun accès internet sur ce réseau: vie privée et données personnelles ne sont accessibles.</p>
                <p>Code source:<br><b>github.com/thierry-g/dj.zic</b></p>
                <form method="post" action="">
                    <input type="hidden" name="accept_cgu" value="Yes">
                    <button id="accept" type="submit" class="action-button">D'accord !</button>
                </form>
            <?php } else { ?>
                <h1>Free Musical Roaming Streaming</h1>
                <h2>Internet</h2>
                <p>This wi-Fi network has no world wide web access. </p>
                <p>It streams the DJ audio in free listening on your smartphone (free data roaming).</p>
                <h2>Security</h2>
                <p>No Internet acces on this network: your personnal data and privacy are unacessible.</p>
                <p>Source code<br>available at: <b>github.com/thierry-g/dj.zic</b></p>
                <form method="post" action="">
                    <input type="hidden" name="accept_cgu" value="Yes">
                    <button id="accept" type="submit" class="action-button">Ok !</button>
                </form>

            <?php } ?>
        </div>
    </div>
    <div id="landscape-message" class="landscape-message">
        <p>Merci, de basculer en mode portrait.</p>
        <svg width="100" height="100" viewBox="0 0 24 24">
            <?php include 'img/landscape.svg'; ?>
        </svg>
        <p>Vous consultez cette page depuis un ordinateur?<br><a href="/computer.php">C'est ici.</a></p>
    </div>
</body>

</html>