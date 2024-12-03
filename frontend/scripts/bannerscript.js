function bannerFunc() {
        const startBanner = document.getElementById('start-banner');
        const playBanner = document.getElementById('play-banner');
        const startGame = document.getElementById('karkuri');

        const players = playerData();
        const firstPlayer = players ? players[0] : null;

        displayBanner(firstPlayer, startBanner, playBanner, startGame);

        // Example usage
       // if (firstPlayer) {
          //  fetchPlayerTickets(firstPlayer.id);
        //    fetchRound(firstPlayer.game_id); // Assuming game_id is available in player data
         //   fetchGameScreenNames(firstPlayer.game_id); // Assuming game_id is available in player data
       // }

}
document.addEventListener('DOMContentLoaded', () => {
    bannerFunc()
})

function playerData() {
    const players = JSON.parse(localStorage.getItem('players'));
    return players;
}

function displayBanner(firstPlayer, startBanner, playBanner, startGame) {
    if (firstPlayer && firstPlayer.type === 0 && firstPlayer.is_computer === 0) {
        startGame.textContent = `${firstPlayer.name}`;
        startBanner.style.display = 'table';
        playBanner.style.display = 'none';
    } else {
        startBanner.style.display = 'none';
        playBanner.style.display = 'table';
    }
}

// Fetch player tickets
export function fetchPlayerTickets(playerId) {
    const potkurikone = document.getElementById('potkurikone');
    const matkustajakone = document.getElementById('matkustajakone');
    const yksityiskone = document.getElementById('yksityiskone');

    fetch(`http://127.0.0.1:3000/api/player-tickets/${playerId}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                potkurikone.textContent = `Potkurikone: ${data.tickets.potkurikone || 0} kpl`;
                matkustajakone.textContent = `Matkustajakone: ${data.tickets.matkustajakone || 0} kpl`;
                yksityiskone.textContent = `Yksityiskone: ${data.tickets.yksityiskone || 0} kpl`;
            } else {
                console.error('Error fetching player tickets:', data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// Fetch round
export function fetchRound(gameId) {
    const roundElement = document.getElementById('kierrokset');

    fetch(`http://127.0.0.1:3000/api/round/${gameId}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                roundElement.textContent = `Round: ${data.round} / 10`;
            } else {
                console.error('Error fetching round:', data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// Fetch game screen names
export function fetchGameScreenNames(gameId) {
    const playerInfoElement = document.getElementById('pelaaja');

    fetch(`http://127.0.0.1:3000/api/game-screen-names/${gameId}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const players = playerData(); // Retrieve players from localStorage
                const screenNames = data.screen_names.map(name => {
                    const player = players.find(p => p.name === name);
                    if (!player) {
                        console.error(`Player with name ${name} not found`);
                        return `Unknown player ${name}`;
                    }
                    return player.type === 0 ? `Rikollisen ${name} vuoro` : `Etsivän ${name} vuoro`;
                });
                playerInfoElement.textContent = screenNames.join(', ');
            } else {
                console.error('Error fetching game screen names:', data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

bannerFunc();