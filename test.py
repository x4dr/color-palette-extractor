from colors.Color import Color
from colors.Theme import Theme

testtheme = Theme([Color.from_rgb(255,0,255).hex], {}, {})


if __name__=="__main__":
    print(testtheme.process_template("KEY(0).HEX"))