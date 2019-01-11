//console.log(election_data[0].fields.name);
var selectElection = document.getElementById("select-election");
var i = 0;
election_data.forEach(function(element) {
  console.log(element);
  var option = document.createElement("option");
  option.text = element.fields.name;
  option.value = element.pk;
  selectElection.add(option, x[i]);
  i+=1;
  //$('.select_election').append( '<option value="'+element.pk+'">'element.fields.name+'</option>');
});
