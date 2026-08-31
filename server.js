const express = require("express");
const cors = require("cors");

const app = express();

app.use(cors());
app.use(express.json({ limit: "20mb" }));

const PORT = process.env.PORT || 3000;


/*
====================================================
 HEALTH CHECK
====================================================
*/

app.get("/", (req, res) => {

    res.json({
        ok: true,
        service: "Telegram Theme Studio",
        status: "online"
    });

});


/*
====================================================
 CREATE THEME DATA
====================================================
*/

app.post("/api/theme", (req, res) => {

    try {

        const {
            name,
            platform,
            colors,
            effects
        } = req.body;


        if (!colors) {

            return res.status(400).json({
                ok: false,
                error: "Colors are required"
            });

        }


        const themeName =
            name ||
            "My Telegram Theme";


        /*
        Telegram-style theme data.

        Пока сервер только принимает
        настройки от Mini App.

        Реальное создание Cloud Theme
        подключим следующим этапом.
        */


        const theme = {

            name: themeName,

            platform:
                platform ||
                "universal",

            colors: {

                background:
                    colors.background ||
                    "#111114",

                header:
                    colors.header ||
                    "#18181d",

                accent:
                    colors.accent ||
                    "#ff4fa3",

                outgoing:
                    colors.outgoing ||
                    "#ff4fa3",

                incoming:
                    colors.incoming ||
                    "#292930",

                text:
                    colors.text ||
                    "#ffffff",

                link:
                    colors.link ||
                    "#ff4fa3",

                secondary:
                    colors.secondary ||
                    "#9999a3"

            },

            effects:
                effects || {}

        };


        res.json({

            ok: true,

            theme: theme,

            message:
                "Theme data received"

        });

    }

    catch (error) {

        console.error(error);

        res.status(500).json({

            ok: false,

            error:
                "Server error"

        });

    }

});


/*
====================================================
 START SERVER
====================================================
*/

app.listen(PORT, () => {

    console.log(
        `Theme Studio server running on port ${PORT}`
    );

});