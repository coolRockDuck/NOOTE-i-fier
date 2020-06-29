import java.io.*
import java.util.*
import java.lang.Exception

const val KEY_ICON_PATH = "ICON_PATH"
const val KEY_NOTES_PATH = "NOTES_PATH"
const val KEY_MINIMAL_SPACE = "MINIMAL_SPACE"
const val KEY_ADDITIONAL_SPACE = "ADDITIONAL_SPACE"

// path to default place where xpad is storing data
val DEFAULT_NOTES_PATH = System.getProperty("user.home") + "/.config/xpad" // this can't be const
const val DEFAULT_MINIMAL_SPACE = "5" // todo simplyfi that system
const val DEFAULT_ADDI_SPACE_AMOUNT = "10"

val prop = getConf()
val config = myProp()

data class myProp constructor(
        val notesPath: String,
        val iconPath: String,
        val minimalSpace: Int,
        val additionalSpace: Int
) {

    constructor(): this(prop.getProperty(KEY_NOTES_PATH, DEFAULT_NOTES_PATH),
                        prop.getProperty(KEY_ICON_PATH),
                        Integer.parseInt(prop.getProperty(KEY_MINIMAL_SPACE, DEFAULT_MINIMAL_SPACE)),
                        Integer.parseInt(prop.getProperty(KEY_ADDITIONAL_SPACE, DEFAULT_ADDI_SPACE_AMOUNT)))
}

fun main(args: Array<String>) {

    var wantHelp = false
    var onlyInCommandLine = false

    for (arg in args) {
        if (arg.startsWith("-")) {
            if (arg.contains('c')) {
                onlyInCommandLine = true
            }
            if (arg.contains('h')) {
                wantHelp = true
            }
        }
    }

    var head: String
    var content: Array<String>
    when {          // you can easily declare how flags change behavior of the script inside 'when'
        wantHelp -> {
            //TODO update instructions how to use this script
            head = "Help";
            content = arrayOf("Help",
                    "How to use: ",
                    "Flags:",
                    "    -c show notes only in command line",
                    "    -h show help",
                    "Config:",
                    "   Go to .config/Notificator to edit config file.",
                    "   You can set or change icon of the notification,",
                    "   change path to where xpad is storing notes,",
                    "   minimal length of notification ",
                    "   and how much notification will be elongated.")
        }

        else -> try {
            head = "TODO"
            content = getNotesContent(config.notesPath)
        } catch (exe: Exception) {
            head = "Error :("
            content = arrayOf(exe.message.toString())
        }
    }

    showNotifi(head, content, onlyInCommandLine)
}

private fun getConf(): Properties {
    val prop = Properties()

    // this script is Linux only so using Path builder is useless because we know file that file name separator is '/'
    val confDir = File(System.getProperty("user.home") + "/" + ".config" + "/" + "Notificator")
    val confFile = File(confDir.absolutePath + "/" + "notificator.conf")

    if (confDir.mkdir() || confFile.createNewFile()) {

        with(prop) {
            setProperty(KEY_ICON_PATH, "CHANGE_ME")
            setProperty(KEY_NOTES_PATH, DEFAULT_NOTES_PATH)
            setProperty(KEY_MINIMAL_SPACE, DEFAULT_MINIMAL_SPACE)
            setProperty(KEY_ADDITIONAL_SPACE, DEFAULT_ADDI_SPACE_AMOUNT.length.toString())
        }

        saveProperties(prop, confFile)
    } else {
        loadProperties(prop, confFile)
    }

//    prop.toList().forEach { println(it) } // TESTING
    return prop
}

fun saveProperties(properties: Properties, file: File) {
    val output = FileOutputStream(file)
    properties.store(output, "Properties for Notificator, if you want icon for your notifications pleas change ICON_PATH")
    output.close()
}

fun loadProperties(properties: Properties, file: File) {
    val input = FileInputStream(file)
    properties.load(input)
    input.close()
}

private fun getNotesContent(path: String): Array<String> {

    val listOfFiles = File(path).listFiles() ?: throw FileNotFoundException(
            "Directory has not been detected")

    for (file: File in listOfFiles) {
        // every note file from xpad with content of the note has 'content' word in the name
        if (!file.name.contains("content")) {
            continue
        }

        val content = file.readLines()
        if (content[0].contains("TODO")) { // first line need to contains 'TODO'
            return content.subList(1, content.size).toTypedArray()
        }
    }

    throw FileNotFoundException("No file with 'content' in name or word 'TODO' in the first line\n"
            + "has been detected in path:\n" + path)
}

private fun showNotifi(head: String, body: Array<String>, onlyInCommandLine: Boolean = false) {

    var lthLongestLine: Int = 0
    body.forEach { line: String ->
        if (lthLongestLine < line.length) {
            lthLongestLine = line.length
        }
    }

    // adding extra length if needed so notification window won`t be too short
    val miniLenght = config.minimalSpace
    if (lthLongestLine < miniLenght && !onlyInCommandLine) {

        val additionalSpace = " ".repeat(config.additionalSpace) //in space characters

        body[0] = body[0] + additionalSpace
    }

    var trueBody = ""
    for (line in body) {
        var copyOfLine = line // creates a copy so we can modify it

        val isGoodLine = (copyOfLine != "" || copyOfLine != "\n")
        if (!isGoodLine) { continue }

        if (line.startsWith("-")) { // we need to add space before '-' character
            copyOfLine = " " + copyOfLine // so notify-send won't threat this as a flag
        }

        if (trueBody == "") { // we need to
            trueBody = trueBody + copyOfLine + "\n"
            continue
        }

        trueBody = trueBody + "\n" + copyOfLine
    }

    if (onlyInCommandLine) {
        println(trueBody)
    } else {
        val icon = File(config.iconPath)
        val command = try {

            if (icon.exists()) {
                arrayOf("notify-send", "-i", icon.absolutePath, head, trueBody)
            } else {
                arrayOf("notify-send", head, trueBody)
            }

        } catch (e: Exception) {
            arrayOf("notify-send", "Error :(", "Pleas check config file, it is probably damaged or missing.")
        }

//        command.forEach { println(it) } // TESTING
        Runtime.getRuntime().exec(command)
    }
}
