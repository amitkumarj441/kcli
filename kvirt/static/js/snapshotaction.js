function snapshotcreate(name){
  var snapshot = prompt("Enter snapshot name");
  if (snapshot == null) {
     return ;
  }
  $("#wheel").show();
  data = {'name': name, 'action': 'create', 'snapshot': snapshot};
  $.ajax({
       type: "POST",
        url: '/snapshotaction',
        data: data,
        success: function(data) {
            $("#wheel").hide();
            if (data.result == 'success') {
                $('.top-right').notify({message: { text: "Snapshot "+snapshot+" Created!!!" }, type: 'success'}).show();
            } else {
                $('.top-right').notify({message: { text: "Snapshot "+snapshot+" Not created because "+data.reason }, type: 'danger'}).show();
            };
        }
    });
}

function snapshotdelete(name){
  data = {'name': name, 'action': 'list'};
  $.ajax({
       type: "POST",
        url: '/snapshotaction',
        data: data,
        success: function(snapshots) {
            if (snapshots.length == 0) {
                $('.top-right').notify({message: { text: "No snapshots found for "+name }, type: 'danger'}).show();
                return
            } else {
                var snapshot = prompt("Choose snapshots between the following ones:\n"+snapshots);
                if (snapshot == null) {
                   return ;
                }
                $("#wheel").show();
                data = {'name': name, 'action': 'delete', 'snapshot': snapshot};
                $.ajax({
                     type: "POST",
                      url: '/snapshotaction',
                      data: data,
                      success: function(data) {
                          $("#wheel").hide();
                          if (data.result == 'success') {
                              $('.top-right').notify({message: { text: "Snapshot "+snapshot+" Deleted!!!" }, type: 'success'}).show();
                          } else {
                              $('.top-right').notify({message: { text: "Snapshot "+snapshot+" Not deleted because "+data.reason }, type: 'danger'}).show();
                          };
                      }
                  });
                          };
                      }
                  });
}

function snapshotrevert(name){
  data = {'name': name, 'action': 'list'};
  $.ajax({
       type: "POST",
        url: '/snapshotaction',
        data: data,
        success: function(snapshots) {
            if (snapshots.length == 0) {
                $('.top-right').notify({message: { text: "No snapshots found for "+name }, type: 'danger'}).show();
                return
            } else {
                var snapshot = prompt("Choose snapshots between the following ones:\n"+snapshots);
                if (snapshot == null) {
                   return ;
                }
                $("#wheel").show();
                data = {'name': name, 'action': 'revert', 'snapshot': snapshot};
                $.ajax({
                     type: "POST",
                      url: '/snapshotaction',
                      data: data,
                      success: function(data) {
                          $("#wheel").hide();
                          if (data.result == 'success') {
                              $('.top-right').notify({message: { text: "Snapshot "+snapshot+" Reverted!!!" }, type: 'success'}).show();
                          } else {
                              $('.top-right').notify({message: { text: "Snapshot "+snapshot+" Not reverted because "+data.reason }, type: 'danger'}).show();
                          };
                      }
                  });
                          };
                      }
                  });
}
