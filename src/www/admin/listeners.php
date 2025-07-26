<div class="icecast hide">
    <?php
    $stats = @json_decode(file_get_contents('/var/www/html/admin/data/stats.json'), true);
    if (!$stats) {
        echo "No data available.";
        exit;
    }
    ?>
    <h1>Audience</h1>
    <ul class="brief">
        <li class="bHeaders">
            <object type="image/svg+xml" data="/img/headset.svg"></object>
            <span class=""><?php echo $stats['global_current'] ?></span>
            <strong>Total</strong>
        </li>
        <li class="bHeaders">
            <object type="image/svg+xml" data="/img/peak.svg"></object>
            <span><?php echo $stats['global_peak'] ?></span>
            <strong>Peak</strong>
        </li>
    </ul>
    <ul class="allListeners">
        <?php foreach ($stats['servers'] as $ip => $s) {
            if (ping($ip)) { ?>
                <li>
                    <object type="image/svg+xml" data="/img/headset.svg"></object>
                    <span><?php echo $s['listeners'] ?></span>
                    <object type="image/svg+xml" data="/img/peak.svg"></object>
                    <?php echo $s['peak'] ?>
                    <span class="ip"><?php echo $ip ?></span>
                </li>
        <?php }
        }
        ?>
    </ul>
</div>