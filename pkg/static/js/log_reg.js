function validate(){
    var user = $("#uname1").val();
    var pass = $("#pass1").val()

    if(user==""){
         document.getElementById("errorMessage").innerHTML='<span class="text-danger"> *fill out all information</span>'
         return false;
     
    }else if(pass==""){
         document.getElementById("errorMessage1").innerHTML='<span class="text-danger"> *fill out all information</span>'
         return false;
     }
    else  {
     document.getElementById("errorMessage").innerHTML=''
     return true;
    }
    
         
    

 }
  $(document).ready(function(){
     $("#change").click(function(){
         $("#formMain").hide();
         $("#logForm").show(700);
     })
     $("#login").click(function(){
         $("#logForm").hide(1000);
         $("#formMain").show(700)
     })
 })
