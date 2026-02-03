import discord

async def not_your(interaction, author_id)-> bool:
    if not interaction.user.id == author_id:
        await interaction.response.send_message(
                "❌ This is not your Casino !",
                ephemeral=True
            )
        return True