console.log("script loaded");

let current = 0;

let selectedScore = null;

let answers = [];
let questions = [] ;

let submitted = false;
fetch("/questions")
.then(r=>r.json())
.then(data=>{

questions=data;

showQuestion();

});

// display questions
function showQuestion(){

document.getElementById("progress").innerHTML=
`Question ${current+1}/${questions.length}`;

document.getElementById("question").innerHTML=
questions[current].text;

let html="";

questions[current].options.forEach(option=>{

html+=`

<div class="option"

onclick="selectOption(this,${option.score})">

${option.text}

</div>

`;

});

document.getElementById("options").innerHTML=html;

selectedScore=null;

}

// select options
function selectOption(element,score){

document.querySelectorAll("option").forEach(

x=>x.classList.remove("selected")

);

element.classList.add("selected");

selectedScore=score;

}

// skip question
document.getElementById("skipBtn")

.onclick=function(){

answers.push(null);

nextQuestion();

}

// next question
document.getElementById("nextBtn")

.onclick=function(){

if(selectedScore===null){

alert("Choose an option or skip.");

return;

}

answers.push(selectedScore);

nextQuestion();

}

// move forward

function nextQuestion(){

if(submitted)
return;
current++;

if(current<questions.length){

showQuestion();

}

else{

submitAnswers();

}

}

// send answers to flask server
function submitAnswers(){

document.querySelector(".card").style.display="none";

    document.getElementById("nextBtn").disabled=true;
    document.getElementById("skipBtn").disabled=true;

    console.log("Answers length =", answers.length);

fetch("/submit",{

method:"POST",

headers:{

"Content-Type":"application/json"

},

body:JSON.stringify({

scores:answers

})

})

.then(r=>r.json())

.then(data=>{
 console.log(data);   
 showResults(data)
 })
.catch(error=>{

        console.log(error);

        document.getElementById("result").innerHTML=
        "<h2>Something went wrong.</h2>";

    });

}

//display results
function showResults(data){

document.querySelector(".card").style.display="none";

document.getElementById("nextBtn").style.display="none";

document.getElementById("skipBtn").style.display="none";

let html="";

html+="<h2>Closest Parties</h2>";

html+="<ol>";

data.closest.forEach(p=>{

html+=`<li>

<b> ${p.party}</b> <br>

Distance : ${p.distance} <br>

Similarity : ${p.similarity}%

</li>

<br>

`;


});

html+="</ol>";

html+=`

<h2>PCA Plot</h2>

<img src="${data.plot}?t=${new Date().getTime()}">

`;

document.getElementById("result").innerHTML=html;

}


