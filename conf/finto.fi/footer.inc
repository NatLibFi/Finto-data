<!-- Piwik -->
<script type="text/javascript">
  var _paq = _paq || [];
  _paq.push(["trackPageView"]);
  _paq.push(["enableLinkTracking"]);

  (function() {
    var u=(("https:" == document.location.protocol) ? "https" : "http") + "://analytics.finto.fi/";
    _paq.push(["setTrackerUrl", u+"piwik.php"]);
    _paq.push(["setSiteId", "1"]);
    var d=document, g=d.createElement("script"), s=d.getElementsByTagName("script")[0]; g.type="text/javascript";
    g.defer=true; g.async=true; g.src=u+"piwik.js"; s.parentNode.insertBefore(g,s);
  })();
</script>
<!-- End Piwik Code -->

<!-- Browser Update -->
<script type="text/javascript">
var $buoop = {reminder: 24, l:'{{ lang }}'}; 
$buoop.ol = window.onload;
window.onload=function(){ 
 try {if ($buoop.ol) $buoop.ol();}catch (e) {}
 var e = document.createElement("script");    
 e.setAttribute("type", "text/javascript");
 e.setAttribute("src", "//browser-update.org/update.js");
 document.body.appendChild(e); 
} 
</script>
<!-- End Browser Update -->
