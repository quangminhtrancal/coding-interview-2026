function isEdge18OrBelow() {
    var isEdge = /Edge\/(\d+)/.test(navigator.userAgent);
    var ver = parseInt(RegExp.$1);

    if (isEdge) {
        document.getElementById('browser-name').innerHTML = 'EDGE';
        document.getElementById('browser-french-name').innerHTML = 'EDGE';
        document.getElementById('browser-and-version').innerHTML = '(Microsoft Edge Version ' + ver + ') ';
        document.getElementById('browser-and-version-french').innerHTML = '(Microsoft Edge Version ' + ver + ') ';
        document.getElementById('device-name').innerHTML = 'a Windows';
        document.getElementById('device-name-fr').innerHTML = 'Windows';
        document.getElementById('edge-windows').style.backgroundColor = '#D9EAFE';
        document.getElementById('logo-user-browser').src = "https://d3azfb2wuqle4e.cloudfront.net/user_uploads/504237/authoring/edge/1623679918144/edge.png";
        document.getElementById('link-to-update').href = "https://www.microsoft.com/en-us/edge";
        document.getElementById('link-to-update-fr').href = "https://www.microsoft.com/en-us/edge";
    }

    return isEdge && ver <= 18;
}

function isChrome70OrBelow() {
    var ua = navigator.userAgent;
    // let isMacDevice = /Mac/i.test(navigator.platform);
    var isChrome = ua.indexOf("Chrome") !== -1 || ua.indexOf("CriOS") !== -1;
    if (isChrome) {
        var version = ua.match(/Chrome\/(\d+)/i);
        if (!version) {
            version = ua.match(/CriOS\/(\d+)/i);
        }//This line is added to avoid loading script issue in ipad chrome
        const versionNumber = parseInt(version[1]);

        document.getElementById('logo-user-browser').src = "https://d3azfb2wuqle4e.cloudfront.net/user_uploads/504237/authoring/chrome-logo/1623679546937/chrome-logo.svg";
        document.getElementById('link-to-update').href = "https://www.google.com/intl/en_ca/chrome/";
        document.getElementById('link-to-update-fr').href = "https://www.google.com/intl/en_ca/chrome/";

        if (/CriOS/i.test(ua) && /iphone|ipod|ipad/i.test(ua)) {
            document.getElementById('browser-name').innerHTML = 'CHROME';
            document.getElementById('browser-french-name').innerHTML = 'CHROME';
            document.getElementById('browser-and-version').innerHTML = '(Google Chrome Version ' + versionNumber + ') ';
            document.getElementById('browser-and-version-french').innerHTML = '(Google Chrome Version' + versionNumber + ') ';
            document.getElementById('device-name').innerHTML = 'an iPad';
            document.getElementById('device-name-fr').innerHTML = 'iPad';
            document.getElementById('chrome-ipad').style.backgroundColor = '#D9EAFE';
            return isChrome && versionNumber <= 74;
        }
        else {
            document.getElementById('browser-name').innerHTML = 'CHROME';
            document.getElementById('browser-french-name').innerHTML = 'CHROME';
            document.getElementById('browser-and-version').innerHTML = '(Google Chrome Version ' + versionNumber + ') ';
            document.getElementById('browser-and-version-french').innerHTML = '(Google Chrome Version ' + versionNumber + ') ';
            if (/Mac/i.test(navigator.platform)) {
                document.getElementById('device-name').innerHTML = 'a macOS ';
                document.getElementById('device-name-fr').innerHTML = 'macOS ';
                document.getElementById('chrome-mac').style.backgroundColor = '#D9EAFE';
            }
            else {
                document.getElementById('device-name').innerHTML = 'a Windows ';
                document.getElementById('device-name-fr').innerHTML = 'Windows ';
                document.getElementById('chrome-windows').style.backgroundColor = '#D9EAFE';
            }

            return isChrome && versionNumber <= 60;
        }
    }
    return false;
}

function isFirefox64OrBelow() {
    var ua = navigator.userAgent;
    var isMacDevice = /Mac/i.test(navigator.platform);
    const isFirefox = ua.indexOf("Firefox") !== -1;
    if (isFirefox) {
        document.getElementById('logo-user-browser').src = "https://d3azfb2wuqle4e.cloudfront.net/user_uploads/504237/authoring/firefox/1623679641116/firefox.png";
        document.getElementById('link-to-update').href = "https://www.mozilla.org/en-CA/firefox/new/";
        document.getElementById('link-to-update-fr').href = "https://www.mozilla.org/en-CA/firefox/new/";
        document.getElementById('change-padding').style.padding ='0 0 3% 3%';
        const version = ua.match(/Firefox\/(\d+)/i);
        console.log(ua)
        if (!version) return false;   //This line is added to avoid loading script issue in ipad chrome
        const versionNumber = parseInt(version[1]);
        document.getElementById('browser-name').innerHTML = 'MOZILLA';
        document.getElementById('browser-french-name').innerHTML = 'MOZILLA';
        document.getElementById('browser-and-version').innerHTML = '(Mozilla Firefox Version ' + versionNumber + ') ';
        document.getElementById('browser-and-version-french').innerHTML = '(Mozilla Firefox Version ' + versionNumber + ') ';
        if (isMacDevice) {
            document.getElementById('device-name').innerHTML = 'a macOS';
            document.getElementById('device-name-fr').innerHTML = 'macOS';
            document.getElementById('firefox-mac').style.backgroundColor = '#D9EAFE';
        } else {
            document.getElementById('device-name').innerHTML = 'a Windows';
            document.getElementById('device-name-fr').innerHTML = 'windows';
            document.getElementById('firefox-windows').style.backgroundColor = '#D9EAFE';
        }
        // return isFirefox && versionNumber <= 64  && versionNumber !== 52; // 52 included to support SEB
        return isFirefox && versionNumber <= 80  && versionNumber !== 52; // 52 included to support SEB
    }
    return false;
}

function isSafari12OrBelow() {
    const vendor = navigator.vendor;
    var ua = navigator.userAgent;
    var isMacDevice = /Mac/i.test(navigator.platform);
    const isSafari = (vendor == "Apple Computer, Inc.");

    if (isSafari) {
        document.getElementById('logo-user-browser').src = "https://d3azfb2wuqle4e.cloudfront.net/user_uploads/504237/authoring/safari-120/1623679818872/safari-120.png";
        document.getElementById('link-to-update').href = "https://support.apple.com/downloads/safari/";
        document.getElementById('link-to-update-fr').href = "https://support.apple.com/downloads/safari/";

        const version = ua.match(/Version\/(\d*\.\d*)/i)
        console.log(ua)
        if (!version) return false;  //This line is added to avoid loading script issue in ipad chrome
        const versionNumber = parseFloat(version[1]);
        document.getElementById('browser-name').innerHTML = 'SAFARI';
        document.getElementById('browser-french-name').innerHTML = 'SAFARI';
        document.getElementById('browser-and-version').innerHTML = '(Apple Safari Version ' + versionNumber + ') ';
        document.getElementById('browser-and-version-french').innerHTML = '(Apple Safari Version ' + versionNumber + ') ';
        if(isMacDevice) {
            document.getElementById('device-name').innerHTML = 'a macOS';
            document.getElementById('device-name-fr').innerHTML = 'macOS';
            document.getElementById('safari-mac').style.backgroundColor = '#D9EAFE';
        } else {
            document.getElementById('device-name').innerHTML = 'an iPad';
            document.getElementById('device-name-fr').innerHTML = 'iPad';
            document.getElementById('safari-ipad').style.backgroundColor = '#D9EAFE';
        }

        // return versionNumber < 12 && versionNumber != '11.1' && versionNumber != '11.0';
        return versionNumber < 10 && versionNumber != '11.1' && versionNumber != '11.0';
    }
    return false;
}

if (/bot|crawler|spider|crawling/i.test(navigator.userAgent)) {
    // noop
} else if (navigator.userAgent.indexOf('MSIE') !== -1 ||
    navigator.appVersion.indexOf('Trident/') > -1 ||
    isEdge18OrBelow() || isChrome70OrBelow() || isFirefox64OrBelow() || isSafari12OrBelow()) {
    /* Microsoft Internet Explorer detected in. */
    var el = document.getElementById('browser-warning');
    el.style.display = 'block';
    el = document.getElementById('loading-overflow');
    el.style.display = 'none';
    el = document.getElementById('app-root');
    el.style.display = 'none';
}

var includeScript = function (url) {
    var js_script = document.createElement('script');
    js_script.type = "text/javascript";
    js_script.src = url;
    js_script.async = true;
    document.getElementsByTagName('head')[0].appendChild(js_script);
}

includeScript('https://d3f6c695rnoy7r.cloudfront.net/lib/zwibbler/v2/zwibbler2.js');
// includeScript('https://unpkg.com/peerjs@1.2.0/dist/peerjs.min.js');
includeScript('https://d3f6c695rnoy7r.cloudfront.net/lib/wavesurfer/4.4.0/dist/wavesurfer-with-mic.js');
// includeScript('https://cdn.rawgit.com/mattdiamond/Recorderjs/08e7abd9/dist/recorder.js');
// includeScript('https://www.geogebra.org/apps/deployggb.js');
includeScript('https://d3azfb2wuqle4e.cloudfront.net/lib/recorder/v1.0/recorder.js');

