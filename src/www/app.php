<?php
session_start();
$lang = substr($_SERVER['HTTP_ACCEPT_LANGUAGE'], 0, 2);
$lang == "fr" ? $lang = "fr" : $lang = "en";
$_SESSION['lang'] = $lang;
if (!isset($_SESSION['accepted_cgu'])) {
    header('Location: index.php', true, 302);
    exit;
} else {
    $_SESSION['submited'] = 0;
} ?>
<!DOCTYPE html>
<html lang="<?php echo $lang ?>">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="fullscreen" content="true">
    <title>Streaming Musical Itinérant</title>
    <link rel="stylesheet" href="/css/djStyle.min.css">
</head>

<body>
    <div class="header">
        <div class="logo"><a href="/admin/"><?php include_once 'img/logo.svg'; ?></a></div>
    </div>
    <div class="content">
        <div class="dj-name">Nom du DJ</div>
        <audio id="audio" class="hide" controls crossorigin="anonymous">
            <source src="http://dj.zic:8000/stream" type="audio/mp3">
            <?php if ($lang == 'fr') { ?>
                <p>Ce Navigateur est incompatible avec HTML5.</p>
                <p>Revenez sur http://dj.zic avec un navigateur mis à jour.</p>
            <?php } else { ?>
                <p>This Browser does not support HTML5.</p>
                <p>Come back http://dj.zic with a most recent browser.</p>
            <?php } ?>
        </audio>
        <canvas id="visualizer" width="320px" height="150"></canvas>
        <div class="stream-info hide" id="stream-info">
            <p class="arrow-paragraph"></p>
        </div>
        <div class="helper" id="help">
            <h2><?php echo $lang == 'fr' ? "Rejoins nous!" : "Join the party!" ?></h2>
            <?php include_once 'help.php'; ?>
        </div>
    </div>
    <div class="controls">
        <button id="shrareBtn" class="share-btn">
            <?php include_once 'img/Invite.svg'; ?>
        </button>
        <button id="playStopBtn" class="play-stop-btn">
            <svg id="playStopIcon" viewBox="0 0 64 64">
                <path id="playIcon" class="playIcon" d="M16 12 L56 32 L16 52 Z" fill="rgb(247,247,247)"></path>
            </svg>
        </button>
        <div class="current-time" id="current-time">0:00</div>
    </div>
    <div id="simpleMsg" class="hide">
        <div class="wrapperMsg">
            <div class="soon hide">
                <h2>Interlude</h2>
                <p><?php
                    echo  $lang = 'fr' ? "La diffusion du stream débute bientôt!" : "The live stream is starting soon!";
                    ?>
                </p>
                <p><?php
                    echo  $lang = 'fr' ? "Le lecteur, s'activera lorsque le stream sera disponible." : "The player button will activate once the Stream begane.";
                    ?></p>
            </div>
            <div class="off hide">
                <h2>
                    <?php
                    echo  $lang = 'fr' ? "Fin de diffusion!" : "End of stream!";
                    ?>
                </h2>
                <p><?php
                    echo  $lang = 'fr' ? "Les serveurs sont hors ligne." : "The servers are off-line.";
                    ?>
                </p>
                <p><?php
                    echo  $lang = 'fr' ? "Vous pouvez supprimer <b>dj.zic</b> des réseaux wi-fi connus." : "You can n ow, remove dj.zic from the known wi-fi networks.";
                    ?>
                </p>
                
                <h3>
                    <?php
                    echo  $lang = 'fr' ? "😄<br>Merci de votre participation.<br>😄" : "😄<br>Thanks for tour participation.<br>😄";
                    ?>
                </h3>
                
            </div>
        </div>
        <!-- button id="refresh-btn" name="Refresh" class="reboot" value="pause">Refresh</button -->
    </div>
    <div id="modal" class="modal">
        <div class="modal-content">
        </div>
    </div>
    <div id="landscape-message" class="landscape-message">
        <p>Merci, de basculer en mode portrait.</p>
        <svg width="100" height="100" viewBox="0 0 24 24">
            <?php include 'img/landscape.svg'; ?>
        </svg>
        <p>Vous consultez cette page depuis un ordinateur?<br><a href="/computer.php">C'est ici.</a></p>
    </div>
    <script src="/js/dj.js"></script>
</body>

</html>