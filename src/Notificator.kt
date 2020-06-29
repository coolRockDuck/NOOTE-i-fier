import java.io.*
import java.util.*
import java.lang.Exception

const val KEY_ICON_PATH = "ICON_PATH"
const val KEY_NOTES_PATH = "NOTES_PATH"
const val KEY_MINIMAL_LENGTH = "MINIMAL_LENGTH"

// path to default place where xpad is storing data
val DEFAULT_NOTES_PATH = System.getProperty("user.home") + "/.config/xpad" // this can't be const
const val DEFAULT_MINIMAL_LENGTH = "10"

val prop = getUserProp()
val config = getConfig()

data class getConfig constructor(
        val notesPath: String,
        val iconPath: String,
        val minimalLength: Int
) {

    constructor(): this(prop.getProperty(KEY_NOTES_PATH, DEFAULT_NOTES_PATH),
                        prop.getProperty(KEY_ICON_PATH),
                        Integer.parseInt(prop.getProperty(KEY_MINIMAL_LENGTH, DEFAULT_MINIMAL_LENGTH)))
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
            head = "Help"
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

    showNotify(head, content.toMutableList(), onlyInCommandLine)
}

private fun getUserProp(): Properties {
    val prop = Properties()

    // this script is Linux only so using Path builder is useless because we know file that file name separator is '/'
    val confDir = File(System.getProperty("user.home") + "/" + ".config" + "/" + "Notificator")
    val confFile = File(confDir.absolutePath + "/" + "notificator.conf")

    if (confDir.mkdir() || confFile.createNewFile()) {

        with(prop) {
            setProperty(KEY_ICON_PATH, "CHANGE_ME")
            setProperty(KEY_NOTES_PATH, DEFAULT_NOTES_PATH)
            setProperty(KEY_MINIMAL_LENGTH, DEFAULT_MINIMAL_LENGTH)
        }

        saveProperties(prop, confFile)
    } else {
        loadProperties(prop, confFile)
    }

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
        if (content.isEmpty()) { continue }

        if (content[0].contains("TODO", ignoreCase = true)) { // first line need to contains 'TODO'
            if (content.size == 1) { return arrayOf("That's all :D") } // file contains only 'TODO'
            return content.subList(1, content.size).toTypedArray()
        }
    }

    throw FileNotFoundException("No file with 'content' in name or word 'TODO' in the first line\n"
            + "has been detected in path:\n" + path)
}

private fun showNotify(header: String, content: MutableList<String>, onlyInCommandLine: Boolean = false) {

    var lthLongestLine = 0
    content.forEach { line: String ->
        if (lthLongestLine < line.length) {
            lthLongestLine = line.length
        }
    }

    // adding extra length if needed so notification window won`t be too short
    val miniLength = config.minimalLength
    for (extraSpace: Int in 0..(miniLength - lthLongestLine)) {
        content[0] = content[0] + " "
    }

    var message = ""
    for (line in content) {
        val isGoodLine = (line != "" || line != "\n")
        if (!isGoodLine) { continue }

        if (line.startsWith("-")) { // we need to add space before '-' character
            message = message + " " + line + "\n" // so notify-send won't threat this as a flag
            continue
        }

        message = message  + line + "\n"
    }

    if (onlyInCommandLine) {
        println(message)
    } else {
        val icon = File(config.iconPath)
        val command = try {

            if (icon.exists()) {
                arrayOf("notify-send", "-i", icon.absolutePath, header, message)
            } else {
                arrayOf("notify-send", header, message)
            }

        } catch (e: Exception) {
            arrayOf("notify-send", "Error :(", "Pleas check config file, it is probably damaged or missing.")
        }

        Runtime.getRuntime().exec(command)
    }
}
