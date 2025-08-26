function filterTable(colIndex) {
    var input = document.querySelectorAll("#prestationsTable thead tr:nth-child(2) input")[colIndex];
    var filter = input.value.toUpperCase();
    var table = document.getElementById("prestationsTable");
    var tr = table.getElementsByTagName("tr");

    for (var i = 2; i < tr.length; i++) { 
        var td = tr[i].getElementsByTagName("td")[colIndex];
        if (td) {
            var txtValue = td.textContent || td.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}
