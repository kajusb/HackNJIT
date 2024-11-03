$(document).ready(function () {
  $("#minimum input,#maximum input").inputmask({
    alias: "decimal",
    digits: 2,
    groupSeparator: ",",
    radixPoint: ".",
    autoGroup: true,
    rightAlign: false,
  });
});
