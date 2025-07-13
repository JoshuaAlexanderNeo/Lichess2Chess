const GAME_TYPES = {
  BLITZ: 'Blitz',
  BULLET: 'Bullet',
  RAPID: 'Rapid',
  CLASSICAL: 'Classical',
  CORRESPONDENCE: 'Correspondence',
  UNKNOWN: 'Unknown'
}

// Fetches regression data from the local JSON file.
const getRegressionData = async () => {
  try {
    const url = chrome.runtime.getURL('regressions.json');
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to fetch regressions: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Error loading regression data:", error);
    return null;
  }
}

// Finds out whether the game is blitz/bullet/rapid or classical
const findGameType = () => {
  let type = document.querySelector('.game__meta__infos');

  if (type !== null) {
    const dataIcon = type.getAttribute('data-icon');
    if (dataIcon === '') {
        return GAME_TYPES.BLITZ;
    } else if (dataIcon === '') {
        return GAME_TYPES.BULLET;
    } else if (dataIcon === '') {
        return GAME_TYPES.RAPID;
    } else if (dataIcon === '') {
        return GAME_TYPES.CLASSICAL;
    } else if (dataIcon === '') {
        return GAME_TYPES.CORRESPONDENCE;
    }
  } 
  return GAME_TYPES.UNKNOWN;
}

// Finds all both ratings in a game
const getLichessRatingsFromGame = () => {
  const rating = document.querySelectorAll('.ruser > rating')
  return rating
}

const getLichessRatingsFromProfile = () => {
  const ratings = document.querySelectorAll('.sub-ratings rating')
  return ratings
}

// Calculates the chess.com rating based on the regression model
const calculateRegression = (regression, lichessRating) => {
    const [p1, p2, p3] = regression.params;
    let result;
    
    switch (regression.type) {
        case 'linear':
            result = Math.round(p1 * lichessRating + p2);
            break;
        case 'quadratic':
            result = Math.round(p2 * lichessRating + p1 * (lichessRating ** 2) + p3);
            break;
        case 'log':
            result = Math.round(p1 * Math.log(lichessRating) + p2);
            break;
        default:
            return null;
    }
    
    // Return 0 if the result is negative (can't have negative ratings)
    return Math.max(0, result);
}

// Adds ratings to the left-most sidebar.
const addChessComRatingToProfile = (lichessRatings, regressions) => {
  for (const rating of lichessRatings) {
    let regression;
    const link = rating.parentElement.parentElement; // This is the <a> tag
    if (!link || link.tagName !== 'A') continue;
    const href = link.getAttribute('href');

    if (href.includes('/perf/bullet')) {
      regression = regressions.BULLET;
    } else if (href.includes('/perf/blitz')) {
      regression = regressions.BLITZ;
    } else if (href.includes('/perf/rapid')) {
      regression = regressions.RAPID;
    } else if (href.includes('/perf/classical')) {
      regression = regressions.CLASSICAL;
    }

    if (regression && !rating.textContent.includes('?')) {
      const lichessRating = parseInt(rating.textContent);
      if (isNaN(lichessRating)) continue;
      const chessComRating = calculateRegression(regression, lichessRating);
      if (chessComRating === null) continue;
      let chessComRatingDiv = document.createElement('span');
      chessComRatingDiv.style.setProperty('color', '#769656');
      chessComRatingDiv.innerText = ` (${chessComRating})`;
      if (rating.firstChild) {
        rating.firstChild.appendChild(chessComRatingDiv);
      }
    }
  }
}

// Adds the chess.com rating equivalent beside the lichess rating.
const addChessComRatingToGame = (gameType, lichessRatings, regressions) => {
  let regression

  if (gameType === GAME_TYPES.BLITZ) {
    regression = regressions.BLITZ
  } else if (gameType === GAME_TYPES.BULLET) {
    regression = regressions.BULLET
  } else if (gameType === GAME_TYPES.RAPID) {
    regression = regressions.RAPID
  } else {
    regression = regressions.CLASSICAL
  }

  for (rating of lichessRatings) {
    const lichessRating = parseInt(rating.innerText)
    const chessComRating = calculateRegression(regression, lichessRating)
    if (chessComRating === null) continue;
    let chessComRatingDiv = document.createElement('div')
    chessComRatingDiv.style.setProperty('color', '#769656')
    chessComRatingDiv.innerText = `(${chessComRating})`
    rating.parentNode.appendChild(chessComRatingDiv)
    rating.parentNode.insertBefore(chessComRatingDiv, rating.nextSibling)
  }

  return lichessRatings
}

const main = async () => {
    const regressions = await getRegressionData();
    if (!regressions) {
        return;
    }

    const gameType = findGameType()
    if (gameType === GAME_TYPES.UNKNOWN) {
      // check if on a profile
      const profileRatings = getLichessRatingsFromProfile()
      addChessComRatingToProfile(profileRatings, regressions)
    } else {
      // in a game, add the chess.com rating to the game
      const lichessRatings = getLichessRatingsFromGame()
      addChessComRatingToGame(gameType, lichessRatings, regressions)
    }
}

main();
