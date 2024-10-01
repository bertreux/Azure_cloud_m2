<?php
// index.php - PHP 8.3 compatible basic file

// Check if the PHP version is compatible
if (version_compare(PHP_VERSION, '8.3.0') >= 0) {
    echo "<h1>Welcome to Azure App Service!</h1>";
    echo "<p>This application is running PHP version " . PHP_VERSION . "</p>";
} else {
    echo "<h1>PHP Version not compatible!</h1>";
    echo "<p>Current PHP version: " . PHP_VERSION . " is not compatible with this app.</p>";
}

// Additional basic content
echo "<p>This is a simple PHP app deployed on Azure using App Service.</p>";
