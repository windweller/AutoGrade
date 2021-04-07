var currentPlayer = 1;
var p1Score=0;
var p2Score=0;

var randButtonId;
setBoard();

function updateScoreBy(amt){
    if(currentPlayer == 1){
        p1Score = p1Score + amt;
    } else {
        p2Score = p2Score + amt;
    }
    setText("score1_label", p1Score);
    setText("score2_label", p2Score);
}

function switchPlayer(){
  if(currentPlayer==1){
    currentPlayer=2;
    showElement("player2_highlight");
    hideElement("player1_highlight");
  } else {
    currentPlayer=1;
    showElement("player1_highlight");
    hideElement("player2_highlight");
  }
}

function setBoard() {
  var R = randomNumber(0, 235);
  var G = randomNumber(0, 235);
  var B = randomNumber(0, 235);
  var color = rgb(R, G, B)

  R += 20;
  G += 20;
  B += 20;

  var diffColor = rgb(R, G, B);

  randButtonId = "button" + randomNumber(1,4);

  setProperty("button1", "background-color", color);
  setProperty("button2", "background-color", color);
  setProperty("button3", "background-color", color);
  setProperty("button4", "background-color", color);
  setProperty(randButtonId, "background-color", diffColor);
}

function checkCorrect(buttonId){
    if(buttonId == randButtonId) {
    	updateScoreBy(1)
    } else {
    	updateScoreBy(-3)
    }
    setBoard();
    switchPlayer();
}

onEvent("button1", "click", function(){
    checkCorrect("button1");
});

onEvent("button2", "click", function(){
    checkCorrect("button2");
});

onEvent("button3", "click", function(){
    checkCorrect("button3");
});

onEvent("button4", "click", function(){
    checkCorrect("button4");
});