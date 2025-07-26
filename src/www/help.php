<?php
session_start();
$lang = $_SESSION['lang'];

if (!isset($_SESSION['accepted_cgu'])) {
    header('Location: index.php', true, 302);
    exit;
} else {
    $_SESSION['submited'] = 0;
}
require_once "admin/inc/tools.php";
function qr_encode($str)
{
    return preg_replace('/(?<!\\\)([\":;,])/', '\\\\\1', $str);
}

if (! file_exists("/var/www/html/img/connect.svg") &&  ! file_exists("/var/www/html/img/connectUrl.svg")) {

    $ssid = qr_encode('dj.zic');
    $password = qr_encode($WIFI);

    $url = "http://dj.zic";

    $data = "WIFI:S:$ssid;T:WPA;P:$password;;";

    $cmd = "qrencode -t svg  -o '/var/www/html/img/connect.svg'  '{$data}'";
    exec($cmd, $out);

    $cmd = "qrencode -t svg  -o '/var/www/html/img/connectUrl.svg'  '$url'";
    exec($cmd, $out);
}

if ($lang == "en") { ?>
    <div class="invite">
        <ol class="steps" id="steps">
            <li class="step" id="step1">
                <svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg" class="disk">
                    <circle style="fill: rgb(52, 13, 117)" cx="16" cy="16" r="12.457" />
                    <text style="fill: rgb(247, 247, 247); font-family: Roboto; font-size: 12px; white-space: pre;" x="13.531" y="20.67">1</text>
                </svg><br>
                <h3>Connecte-toi au point d'accès</h3>
                <div style="display:inline-flex;flex-direction: column;align-items: center;padding:.96rem;">
                    <h4>dj.zic</h4>
                    <?php include_once '/var/www/html/img/connect.svg';  ?>
                </div>
                <p>Pour ne pas être déconnecté lors des déplacements, nous conseillons d'activer la connextion automatique à ce réseau.</p>
            </li>
            <li class="step" id="step2">
                <svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg" class="disk">
                    <circle style="fill: rgb(52, 13, 117)" cx="16" cy="16" r="12.457" />
                    <text style="fill: rgb(247, 247, 247); font-family: Roboto; font-size: 12px; white-space: pre;" x="13.531" y="20.67">2</text>
                </svg><br>
                <h3>Accès au stream</h3>


                <div style="display:inline-flex;flex-direction: column;align-items: center;padding:.96rem;">
                    <h4>http://dj.zic</h4>
                    <?php include_once '/var/www/html/img/connectUrl.svg'; ?>
                </div>
                <p>Ouvrez le navigateur sur la page d'écoute du steam. N'oubliez pas vos 🎧 ;-) 🥳</p>
            </li>

            </li>
        </ol>
    </div><?php
        } else { ?>
    <div class="invite">
        <ol class="steps" id="steps">
            <li class="step" id="step1">
                <svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg" class="disk">
                    <circle style="fill: rgb(52, 13, 117)" cx="16" cy="16" r="12.457" />
                    <text style="fill: rgb(247, 247, 247); font-family: Roboto; font-size: 12px; white-space: pre;" x="13.531" y="20.67">1</text>
                </svg>
                <h3>Connecte-toi au point d'accès</h3>
                <div style="display:inline-flex;flex-direction: column;align-items: center;padding:.96rem;">
                    <h4>dj.zic</h4>
                    <?php include_once '/var/www/html/img/connect.svg';  ?>
                </div>
                <p>Pour ne pas être déconnecté lors des déplacements, nous conseillons d'activer la connextion automatique à ce réseau.</p>
            </li>
            <li class="step" id="step2">
                <svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg" class="disk">
                    <circle style="fill: rgb(52, 13, 117)" cx="16" cy="16" r="12.457" />
                    <text style="fill: rgb(247, 247, 247); font-family: Roboto; font-size: 12px; white-space: pre;" x="13.531" y="20.67">2</text>
                </svg>
                <h3 style="margin-right: 11rem;">Accès au stream</h3>
                <div style="display:inline-flex;flex-direction: column;align-items: center;padding:.96rem;">
                    <h4>http://dj.zic</h4>
                    <?php include_once '/var/www/html/img/connectUrl.svg'; ?>
                </div>
                <p>Ouvre votre navigateur sur la page d'écoute du steam. N'oubliez pas vos 🎧 ;-) 🥳</p>
            </li>

        </ol>
    </div>
<?php } ?>




<div class="dots" id="dots">
    <div class="dot active"></div>
    <div class="dot"></div>
</div>