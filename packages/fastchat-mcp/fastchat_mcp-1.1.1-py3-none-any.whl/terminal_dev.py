from fastchat import TerminalChat

chat = TerminalChat(
    extra_reponse_system_prompts=[
        "Eres un NPC de un vendedor ambulante para un juego RPG. Debes comportarte como tal y dar tus respuestas acorde a tu personaje. Te dedicas a la venta de armamento medieval, como espadas, armaduras, escudos y otros. Dirigete  quien te hable como si ese usuario fuera un aventurero en un mundo medieval de fantasia."
    ],
    aditional_servers={
        "github": {
            "protocol": "httpstream",
            "httpstream-url": "https://api.githubcopilot.com/mcp",
            "name": "github",
            "description": "This server specializes in github operations.",
            "headers": {
                "Authorization": "Bearer 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"
            },
        }
    },
)
chat.open()
