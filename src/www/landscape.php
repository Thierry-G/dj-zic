<div id="landscape-message" class="landscape-message">
<?php

if ($lang == "fr") 
{ ?>
    <p>Merci, de basculer en mode portrait.</p>
    <svg width="100" height="100" viewBox="0 0 24 24">
        <?php include 'img/landscape.svg'; ?>
    </svg>
    <p>Vous consultez cette page depuis un ordinateur?<br><a href="/<?php echo $url;?>">C'est ici.</a></p>
<?php
} 
else 
{ ?>
    <p>Thanks to switch in portrait mode.</p>
    <svg width="100" height="100" viewBox="0 0 24 24">
        <?php include 'img/landscape.svg'; ?>
    </svg>
    <?php 
    $url = (isset($_GET['from']) && $_GET['from'] == 'admin') ? 'computer.php?from=admin' :  'computer.php';
    ?>
    <p>Are you browsing here from a computer?<br><a href="/<?php echo $url;?>">It's here.</a></p>
<?php 
} ?>
</div>