const { Client } = require('discord.js-selfbot-v13');
const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));
require('dotenv').config();
const client = new Client({
    checkUpdate: false
}); // All partials are loaded automatically

client.on('ready', async () => {
  console.log(`${client.user.username} is ready!`);
})

const PlaceIdRegex = new RegExp(/games\/(\d+)/);
const ServerLinkCodeRegex = new RegExp(/\?privateServerLinkCode=([\w-]*)/);
var AlreadyCheckedLinks = []
var BlacklistedGames = [
    6516141723,
    920587237,
    4623386862,
    3095204897,
    8737602449,
    863266079,
    8304191830,
    2971329387,
    2537430692,
    5670218884
]

client.on('messageCreate', async message => {
    var PlaceIdResults = message.content.match(PlaceIdRegex)
    var ServerLinkCodeResults = message.content.match(ServerLinkCodeRegex)
    if (PlaceIdResults && ServerLinkCodeResults) {

        if (BlacklistedGames.includes(parseInt(PlaceIdResults[1]))) {
            console.log(`Recieved VIP server link which is blacklisted { ${PlaceIdResults[1]} } in [ ${message.guild.name} ] by ( ${message.author.username}#${message.author.discriminator} )`)
            return;
        }

        var CombinedLink = `https://www.roblox.com/games/${PlaceIdResults[1]}?privateServerLinkCode=${ServerLinkCodeResults[1]}`
        if (AlreadyCheckedLinks.includes(CombinedLink)) {
            return
        }
        AlreadyCheckedLinks.push(CombinedLink)
        console.log(`Found VIP Server Link: ${CombinedLink} in [ ${message.guild.name} ] by ( ${message.author.username}#${message.author.discriminator} )`)

        fetch(
            'https://rbxservers.xyz/api/share-vip', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    "link": CombinedLink
                })
            }
        )

        fetch(
            process.env.DISCORD_WEBHOOK, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    "content": `Found VIP Server Link: ${CombinedLink} in [ **${message.guild.name}** ] by ( **${message.author.username}#${message.author.discriminator}** )`,
                    "username": `VIP Server Finder [ ${message.guild.name} ]`
                })
            }
        )
    }
})

client.login(process.env.DISCORD_TOKEN);