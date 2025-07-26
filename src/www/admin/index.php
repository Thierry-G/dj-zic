<?php
session_start();
require "inc/tools.php";

if (isset($_SESSION['auth'])) {
    if ($_SESSION['auth'] === true) {
        $_SESSION['submited'] = 0;
    }
} else {
    header('Location: login.php');
    exit;
}

$lang = "en"; #$_SESSION['lang']

$djName = '';
$prev = null;
$bgImage = null;
$changeBg = false;
$currStatus = getFileJsonData($STATUS);
$config     = getFileJsonData($CONFIG);
$streamInfo = getFileJsonData($STREAM);

$curr = $streamInfo['stream']['src'];

if (!isset($_SESSION['curr_src'])) {
    $_SESSION['curr_src'] = $curr;
    $_SESSION['prev_src'] = null;
} elseif ($_SESSION['curr_src'] !== $curr) {
    // Update previous only if stream source changed
    $_SESSION['prev_src'] = $_SESSION['curr_src'];
    $_SESSION['curr_src'] = $curr;
}

function displayStatus($type, $desc, $data, $isLocal = true, $ip = '')
{
    $out      = '';
    $allOn    = true;
    $offCount = 0;
    foreach ($data as $service => $status) {
        if ($status !== 'na') {
            $description =  htmlspecialchars($desc[$service], ENT_QUOTES, 'UTF-8');
            $statusText  = $status === 1 ? 'Ok' : 'Off';
            $statusClass = $status === 1 ? 'status-on' : 'status-off';

            $out .= "<div class='service'><span class='serviceName'>$description</span><span class='$statusClass'>$statusText</span>";
            if ($status === 0) {
                $out .= " <button onclick=\"restartService('$service', " . ($isLocal ? 'true' : 'false') . ", '$ip','$description')\" class=\"alert\">Restart</button>";
                $allOn = false;
                $offCount++;
            } else {
                $out .= " <button onclick=\"restartService('$service', " . ($isLocal ? 'true' : 'false') . ", '$ip','$description')\">Restart</button>";
            }
            $out .= "</div>";
        }
    }
    $out .= "<div class='options'><button class='reboot' onclick=\"rebootServer('$type'," . ($isLocal ? 'true' : 'false') . ", '$ip')\">Redémarrer</button></div>";
    return ['html' => $out, 'allOn' => $allOn, 'offCount' => $offCount];
}

$isApple = detectiOS();

if (! isset($_SESSION['GUI'])) {
    $_SESSION['GUI']['Tab'] = 'Stream';
}

if (isset($_SESSION['upBg'])) {
    $bgImage = "/admin/uploads/" . $_SESSION['upBg'] . ".jpg";
    $changeBg = true;
    unset($_SESSION['upBg']);
} else {
    $bgImage  = "/admin/uploads/" . $streamInfo['stream']['src'];

    switch ($streamInfo['stream']['live']) {
        case 'validation':

            if (file_exists($bgImage)) {
                $changeBg = true;
                $streamInfo['stream']['live'] = 'true';
                saveJsonData($streamInfo, $STREAM);
            } else {
                $bgImage = null;
                $changeBg = false;
            }

        case 'true':
            if (!file_exists("/admin/uploads/" . $streamInfo['stream']['src'])) {
                if ($streamInfo['stream']['id'] == 'default') {
                    $bgImage = null;
                } else {
                    $bgImage  = "/admin/uploads/" .  $_SESSION['curr_src'];
                }
            } else {
                $bgImage  = "/admin/uploads/" . $_SESSION['curr_src'];
            }
            $changeBg = true;
            break;

        case 'false':
            if (file_exists($bgImage)) {
                $changeBg = true;
            }
            $changeBg = false;
            break;
        default:
            $bgImage  = "/admin/uploads/" . $streamInfo['stream']['src'];
            $changeBg = false;
            break;
    }
}
?>
<!DOCTYPE html>
<html lang="<?php echo $lang ?>">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DJ Administration</title>
    <link rel="stylesheet" href="/css/admin.min.css" />
    <?php
    //echo  file_exists("/var/www/html/".$bgImage);
    if ($changeBg === true && $bgImage !== null && file_exists("/var/www/html/" . $bgImage)) {
        echo <<<EOF
            <style>
            .upBg { background: url('$bgImage') no-repeat center center; background-size: cover; }
            </style>
        EOF;
    } else if (! file_exists("/var/www/html/" . $bgImage)) {
        $bgImage = "/admin/uploads/" . $streamInfo['stream']['id'] . ".jpg";
        echo <<<EOF
            <style>
            .upBg { background: url('$bgImage') no-repeat center center; background-size: cover; }
            </style>
        EOF;
    ?>
    <?php
    } ?>
</head>
<?php

if ($_SESSION['GUI']['Tab'] == "System" || $_SESSION['GUI']['Tab'] == "Party") {
    $bg = "noBg";
} elseif ($changeBg === true) {
    $bg = "upBg";
} else {
    $bg = "";
}
?>

<body class="<?php echo $bg; ?>" data-prev="<?php echo $_SESSION['prev_src'] ?>" data-curr="<?php echo $_SESSION['curr_src'] ?>">
    <div id="actionScreen" class="hide">

        <div id="AddPict" class="pictContainer hide">
            <div class="step active" id="step1">
                <h1><?php
                    echo $lang == 'fr' ? "Selectionner la photo" : "Select the photo";
                    ?></h1>
                <?php if ($isApple) { ?>
                    <p id="iosInfo"><img src="/img/ios.svg" width="48px" alt="IOS"><?php
                                                                                    if ($lang == "fr") { ?>Photographier, avant d'ajouter la photo à partir de la photothèque !
                        <?php } else { ?>Take the picture before, and add it from the photo library!<?php } ?>
                    </p>
                    <?php } else {
                    if ($lang == "fr") { ?><p class="instructions">Choisissez une image à partir de la photothèque de l'appareil.</p>
                    <?php } else { ?> <p class="instructions">Choose a picture from the photo library.</p> <?php }
                                                                                                    } ?>
                <input type="file" id="imageInput" accept="image/*" style="display: none;">
                <button class="btn" id="selectImageBtn"><?php echo $lang == 'fr' ? "Choisir la photo" : "Choose a photo"; ?></button>
            </div>

            <div class="step" id="step2">
                <div id="imagePreviewContainer">
                    <div id="imageWrapper">
                        <img id="selectedImage" src="" alt="Selected Image">
                        <div id="cropFrame">
                            <div class="resize-handle" id="resizeHandleTL"></div>
                            <div class="resize-handle" id="resizeHandleTR"></div>
                            <div class="resize-handle" id="resizeHandleBL"></div>
                            <div class="resize-handle" id="resizeHandleBR"></div>
                        </div>
                    </div>
                </div>
                <div class="btns">
                    <button class="action-upload" id="cropDoneBtn">OK</button>
                    <button id="closeButtonA" class="action-cancel"><?php echo $lang == 'fr' ? "Annuler" : "Cancel"; ?></button>
                </div>
            </div>
            <button id="closeAddPict" class="close" title="Annuler"><?php echo $lang == 'fr' ? "Fermer" : "Close"; ?></button>
            <div class="btns hide" id="step3">
                <object id="cropWait" type="image/svg+xml" data="/img/wait.svg" class="hide"></object>
                <button id="validateButton" class="action-validate"><?php echo $lang == 'fr' ? "Valider" : "Validate"; ?></button>
                <button id="closeButtonB" class="action-cancel"><?php echo $lang == 'fr' ? "Annuler" : "Cancel"; ?></button>
            </div>
            <script src="js/imageCrop.js" type="module"></script>
        </div>

        <div id="ManagePict" class="hide">
            <div class="wrap-container">
                <h1><?php
                    echo $lang == 'fr' ? "Modifier" : "Modify"
                    ?></h1>
                <?php
                $logFilePath = 'uploads/upload_log.json';
                $logData = [];

                if (file_exists($logFilePath)) {
                    $logData = json_decode(file_get_contents($logFilePath), true);
                }
                // Chart 
                $folderPath = '/var/www/html/admin/uploads';
                $diskPath = '/';
                $folderSize = getFolderSize($folderPath); //
                $diskTotalSize = getDiskTotalSize($diskPath);
                $allocatedSpace = $diskTotalSize * 0.05; // 5% allocated space
                $folderPercentage = ($folderSize / $diskTotalSize) * 100;
                $allocatedPercentage = ($allocatedSpace / $diskTotalSize) * 100;
                $remainingSpace = $diskTotalSize - $folderSize - $allocatedSpace;

                ?>
            </div>
            <div class="chart-container" id="chart" data-size="<?php echo $diskTotalSize; ?>">
                <canvas id="doughnutChart" width="100" height="100"></canvas>

                <div class="text-info">
                    <h3><?php echo $lang == 'fr' ? "Espace disque" : "Disk space"; ?></h3>
                    <h4><?php echo $lang == 'fr' ? "Utilisé" : "Used"; ?>:
                        <span id="folderSize" data-size="<?php echo $folderSize; ?>">
                            <?php
                            echo ($folderSize < (1024 * 1024 * 1024))
                                ? round($folderSize / (1024 * 1024), 2) . " Mo"
                                : round($folderSize / (1024 * 1024 * 1024), 2) . " Go";
                            ?>
                        </span>
                    </h4>

                    <h4><?php echo $lang == 'fr' ? "Disponible" : "Available"; ?>:
                        <span id="allocatedSpace" data-size="<?php echo $allocatedSpace; ?>">
                            <?php
                            echo ($allocatedSpace < (1024 * 1024 * 1024))
                                ? round($allocatedSpace / (1024 * 1024), 2) . " Mo"
                                : round($allocatedSpace / (1024 * 1024 * 1024), 2) . " Go";
                            ?>
                        </span>
                    </h4>

                    <h4><?php echo $lang == 'fr' ? "Restant" : "Remaining"; ?>:
                        <span id="remainingSpace" data-size="<?php echo $remainingSpace; ?>">
                            <?php

                            echo ($remainingSpace < (1024 * 1024 * 1024))
                                ? round($remainingSpace / (1024 * 1024), 2) . " Mo"
                                : round($remainingSpace / (1024 * 1024 * 1024), 2) . " Go";
                            ?>
                        </span>
                    </h4>
                </div>

            </div>
            <div id="carousel" class="">
                <?php
                if ($streamInfo['stream']['id'] == 'default') { ?>
                    <div class="vignette current" style="<?php echo setBgurl('/img/default.png') ?>" id="default">
                        <div class="action">
                            <span
                                class="current <?php echo $streamInfo['stream']['id'] == 'default' ? '' : 'hide'; ?>"></span>
                        </div>
                        <div class="stamp"><?php echo $lang == 'fr' ? "Illustration par défaut" : "Default"; ?>.</div>
                    </div>
                <?php } else { ?>
                    <div class="vignette" style="<?php echo setBgurl('/img/default.png') ?>" id="default">
                        <div class="action">
                            <button type="submit" name="setCurrent" class="setCurrent" title="<?php echo $lang == 'fr' ? "Choisir comme fond d'écran" : "Choose as wallpaper"; ?>"
                                onclick="setCurrentBg('default');"></button>
                        </div>
                        <div class="stamp"><?php echo $lang == 'fr' ? "Illustration par défaut" : "Default"; ?>.</div>
                    </div>
                    <?php
                }

                foreach ($logData as $entry):
                    $path = '/admin/uploads/' . $entry['file'];
                    $id = pathinfo($entry['file'], PATHINFO_FILENAME);

                    if (file_exists('/var/www/html/admin/uploads/' . $entry['file'])) {


                        if ($streamInfo['stream']['id'] . ".jpg" === $entry['file']) { ?>
                            <div class="vignette current" style="<?php echo setBgurl($path); ?>" id="<?php echo $id; ?>">
                                <div class="action">
                                    <span class="current"></span>
                                </div>
                                <div class="stamp">
                                    <?php echo formatDateTime($entry['date']); ?>
                                </div>
                            </div>
                        <?php } else { ?>
                            <div class="vignette" style="<?php echo setBgurl($path); ?>" id="<?php echo $id; ?>">
                                <div class="action">
                                    <button type="submit" name="Delete" class="delete" title="<?php echo $lang == 'fr' ? "Supprimer" : "Delete"; ?>"
                                        onclick="deleteBg('<?php echo $id; ?>');"></button>
                                    <button type="submit" name="setCurrent" class="setCurrent" title="<?php echo $lang == 'fr' ? "Choisir comme fond d'écran" : "Choose as wallpaper"; ?>"
                                        onclick="setCurrentBg('<?php echo $id; ?>');"></button>
                                </div>
                                <div class="stamp">
                                    <?php echo formatDateTime($entry['date']); ?>
                                </div>
                            </div>

                <?php }
                    }
                endforeach;
                ?>

            </div>
            <button id="closePictMgt" class="close" title="Annuler"></button>
        </div>
    </div>
    <div class="header  <?php echo $_SESSION['GUI']['Tab'] === "System" ? 'wBg' : '' ?>">
        <div class="logo">
            <a href="/"><?php include_once '../img/logo.svg'; ?></a>
        </div>
        <h1 class="mg"><a href="/">M.C. Admin.</a></h1>
        <div class="wrapper">
            <div id="streamers">
                <?php include_once '../img/streamers.svg'; ?>
                <span id="totalStreamers">--</span>
            </div>
        </div>
        <?php include "listeners.php" ?>
    </div>

    <div class="content">

        <div id="rightMenu" class="<?php echo $_SESSION['GUI']['Tab'] === "Stream" ? '' : 'hide'; ?>">

            <div id="djNameMenu" class="closed">
                <h2 class="">
                    <?php
                    $djName = $currStatus['stream']['dj'];
                    echo $currStatus['stream']['dj']; ?>
                </h2>

                <div id="djNameEdit" class="closed">
                    <button id="djNameBtn"><?php include_once "../img/edit.svg" ?></button>
                    <div class="modify selected hide">
                        <textarea type="text" id="djNameInput" class="selected hide"><?php echo $djName; ?></textarea>
                        <div id="djNameError" class="error hide"></div>
                        <div class="charCount">
                            <p class="right"><span id="charCount">0</span> /144</p>
                        </div>

                        <div class="btn-grp">
                            <div class="wrapperBtn">
                                <button id="ActionChangeDjName" class="action-button">Ok</button>
                                <object type="image/svg+xml" data="/img/wait.svg" class="hide"></object>
                                <button id="djNameClose" class="close" title="<?php echo $lang == 'fr' ? "Annuler" : "Cancel"; ?>"></button>
                            </div>
                        </div>
                    </div>
                </div>


            </div>

            <div id="djPictMenu" class="closed">
                <!-- closed -->
                <button id="djPictBtn" class=""><?php include_once "../img/camera.svg"; ?></button>
                <div id="djPictEdit" class="modify hide">
                    <ul class="modify selected">
                        <li>
                            <button id="djPict" title="<?php echo $lang == 'fr' ? "Ajouter" : "Add"; ?>" class="modify action-button <?php echo $lang; ?>" value="<?php echo $lang == 'fr' ? "Ajouter" : "Add"; ?>"></button>
                        </li>
                        <li>
                            <button id="pictMgt" title="<?php echo $lang == 'fr' ? "Modifier" : "Modify"; ?>" class="modify action-button <?php echo $lang; ?>" value="<?php echo $lang == 'fr' ? "Modifier" : "Modify"; ?>"></button>
                        </li>
                    </ul>
                    <button id="djPictClose" class="close" title="<?php echo $lang == 'fr' ? "Annuler" : "Cancel"; ?>"></button>
                </div>
            </div>

            <div class="wrapperStart">
                <button id="eventStart" title="<?php echo $lang == 'fr' ? "Pause" : "Pause"; ?>" class="<?php echo $lang; ?>" value="start"></button>
            </div>
        </div>
        <div id="SystemMngt" class="<?php echo $_SESSION['GUI']['Tab'] === "System" ? '' : 'hide'; ?>">


            <div id="services" class="hide">
                <div class='options all'>
                    <h4><?php echo $lang == 'fr' ? "Rédémarrer tous les appareils\n du réseau" : "Reboot all the devices "; ?></h4>

                    <button class='reboot' id="rebootAll"><?php echo $lang == 'fr' ? "D'accord" : "Ok"; ?></button>
                </div>
                <?php
                if ($_SESSION['GUI']['Tab'] === "System") {
                    $thisPi = '';
                    $out    = '';
                    foreach ($config['servers'] as $server) {

                        if (getWlan0Ip() === $server['ip']) {
                            $status       = displayStatus($server['type'][$lang], $config['description'][$lang], $currStatus['services'], true);
                            $chevronClass = $status['allOn'] ? 'collapsed' : '';
                            $displayStyle = $status['allOn'] ? 'collapsed' : 'flex';
                            $offIndicator = $status['offCount'] > 0 ? '🟠' : '';
                            $thisPi .= "<div class=\"server\">";
                            $thisPi .= "    <div class=\"server-header\" onclick=\"toggleServiceList(this);\">";
                            $thisPi .= "    <span class=\"ip\">" . $server['ip'] . "</span>";
                            $thisPi .= "    <span class=\"left\">" . $server['name'] . "</span>";
                            $thisPi .= "    <br><span class=\"left serverType\">" . $server['type'][$lang] . "</span>";
                            $thisPi .= "        <span class=\"chevron $chevronClass\">˄</span>";
                            $thisPi .= "    </div>";
                            $thisPi .= "    <div class=\"service-list\" style=\"display:" . $displayStyle . "\">" . $status['html'] . "</div>";
                            $thisPi .= '</div>';
                        } else if (ping($server['ip'])) {
                            $services = getUrlJsonData($server['ip']);
                            $status   = displayStatus($server['type'], $config['description'][$lang], $services['services'], false, $server['ip']);

                            $chevronClass = $status['allOn'] ? 'collapsed' : '';
                            $displayStyle = $status['allOn'] ? 'collapsed' : 'flex';
                            $offIndicator = $status['offCount'] > 0 ? '🟠' : '';
                            $out .= "<div class=\"server\">";
                            $out .= "    <div class=\"server-header\" onclick=\"toggleServiceList(this);\">";
                            $out .= "    <span>" . $server['ip'] . "</span>";
                            $out .= "    <span>" . $server['name'] . "</span>";
                            $out .= "    <br><span class=\"left serverType\">" . $server['type'][$lang] . "</span>";
                            $out .= "        <span class=\"chevron $chevronClass\">˄</span>";
                            $out .= "    </div>";
                            $out .= "    <div class=\"service-list\" style=\"display:" . $displayStyle . "\">" . $status['html'] . "</div>";
                            $out .= '</div>';
                        }
                    }
                    echo "$thisPi$out";
                }
                ?>
                <script>
                    document.addEventListener("DOMContentLoaded", function() {
                        setTimeout(() => {
                            document.getElementById("loadingServices").classList.toggle('hide');
                            document.getElementById("services").classList.toggle('hide');

                        }, 500);
                    });
                </script>
            </div>
        </div>
        <div id="PartyMngt" class="<?php echo $_SESSION['GUI']['Tab'] === "Party" ? '' : 'hide'; ?>">
            <div class="wrapper">
                <h2><?php
                    echo $lang == 'fr' ? "Désactiver/Activer les Hauts parleurs" : "Activate / deactivate speakers";
                    ?></h2>
                <div id="svgContainer">
                    <?php include_once '../img/speakers.svg'; ?>
                </div>
                <button id="cutSound" title="<?php echo $lang == 'fr' ? "Et, je coupe le son" : "Speaker off"; ?>" class="action-button cutSound <?php echo $lang; ?>" value="mute">
                    <?php echo $lang == 'fr' ? "Et, je coupe le son" : "Speaker off"; ?>...</button>
            </div>

            <div class="wrapper">
                <h2><?php
                    echo $lang == 'fr' ? "Déambuler en cortège" : "Ride in cortege";
                    ?></h2>
                <div class="switch-container">
                    <h3 class="switch-label">Radar</h3>
                    <label class="switch"><?php
                                            $swiched = '';
                                            if (isset($_SESSION['Radar'])) {
                                                switch ($_SESSION['Radar']) {
                                                    case 'on':
                                                        $swiched = 'checked';
                                                        break;
                                                }
                                            } ?>
                        <input type="checkbox" id="switchToggle" <?php echo $swiched ?>>
                        <span class="slider">
                            <span class="label-on">On</span>
                            <span class="label-off">Off</span>
                        </span>
                    </label>

                </div>
                <p id="switchMessage">
                    <?php
                    echo $lang == 'fr' ?  "Activer le radar ouvre un nouvel onglet." : "Radar activation opens a new tab.";
                    ?></p>
            </div>
            <div class="wrapper">
                <h2><?php echo $lang == 'fr' ? "Eteindre tous les Raspberries" : "Shutdown all Raspberries"; ?></h2>
                <button id="endParty" title="<?php echo $lang == 'fr' ? "Eteindre" : "Shutdown"; ?>" class="action-button shudown <?php echo $lang; ?>"></button>
            </div>
        </div>

    </div>

    <div class="footer">
        <ul>
            <li id="TabSound" class="<?php echo $_SESSION['GUI']['Tab'] === "Stream" ? 'active' : ''; ?>">
                <button id="stream" value="Stream" title="Stream" class="<?php echo $_SESSION['GUI']['Tab'] === "Stream" ? 'active' : ''; ?>"></button>
            </li>
            <li id="TabSystem" class="<?php echo $_SESSION['GUI']['Tab'] === "System" ? 'active' : ''; ?> ">
                <button id="system" value="System" title="System" class="<?php echo $lang; ?> <?php echo $_SESSION['GUI']['Tab'] === "System" ? 'active' : ''; ?>"></button>
            </li>
            <li id="TabParty" class="<?php echo $_SESSION['GUI']['Tab'] === "Party" ? 'active' : ''; ?>">
                <button id="party" value="Party" title="Party" class="<?php echo $_SESSION['GUI']['Tab'] === "Party" ? 'active' : ''; ?>"></button>
            </li>
        </ul>

    </div>
    <div id="loadingServices">
        <object type="image/svg+xml" data="/img/wait.svg"></object>
        <p>Loading...</p>
    </div>
    <div id="modal" class="modal hide">
        <div class="modal-content hide"></div>
        <div class="modal-confirm hide">
            <h1>Confirmer</h1>
            <p id="confirm"></p>
            <div class="buttons">
                <button id="confirmButton" class="action-button"><?php echo $lang == 'fr' ? "Oui" : "Yes"; ?></button>
                <button id="cancelButton" class="action-cancel"><?php echo $lang == 'fr' ? "Non" : "No"; ?></button>
            </div>
        </div>
    </div>
    <div id="progressBarContainer" class="hide">
        <span><?php echo $lang == 'fr' ? "Téléchargement en cours" : "Uploading"; ?>...</span>
        <div id="progressBar"></div>
    </div>
    <script src="js/admin.js" type="module"></script>

</body>

</html>