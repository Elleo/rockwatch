import QtQuick 1.1;
import Qt 4.7
import com.nokia.meego 1.0;

PageStackWindow {
	id: rootWin;
	property int pageMargin: 16;

	Component.onCompleted: {
		theme.inverted = true;
	}

	signal ping();
	signal quit();

	function showMessage(title, message, quitAfter) {
		if(quitAfter) {
			quitDialog.titleText = title;
			quitDialog.message = message;
			quitDialog.open();
		} else {
			messageDialog.titleText = title;
			messageDialog.message = message;
			messageDialog.open();
		}
	}

	function startWorking() {
		indicator.running = true;
		indicator.opacity = 1;
	}

	function stopWorking() {
		indicator.running = false;
		indicator.opacity = 0;
	}

	function connected() {
		connected.visible = true;
		watchImg.opacity = 1;
	}

	function clearStatus() {
		status.text = "";
	}

	function setStatusPlaceholder(placeholder) {
		status.placeholderText = placeholder;
	}

	function showBack() {
		backIcon.visible = true;
		rootWin.showFetch = false;
	}

	function hideBack() {
		backIcon.visible = false;
		rootWin.showFetch = true;
	}

	function openFile(file) {
		var component = Qt.createComponent(file);
		if (component.status == Component.Ready) {
			pageStack.push(component);
		} else {
			console.log("Error loading component:", component.errorString());
		}
	}

	Image {
		id: watchImg;
		source:	"../watch.png";
		opacity: 0.25;
		Behavior on opacity { PropertyAnimation { duration: 1000 } }
		anchors.centerIn: parent;
		MouseArea {
			anchors.fill: parent;
			onClicked: {
				toolMenu.open();
			}
		}
	}

	Label {
		id: connected;
		text: "Connected";
		anchors.centerIn: parent;
		visible: false;
	}

	BusyIndicator {
		id: indicator
		platformStyle: BusyIndicatorStyle { size: "large" }
		running:  false;
		Behavior on opacity { PropertyAnimation { duration: 100 } }
		opacity: 0;
		anchors.centerIn: parent;
	}

	Menu {
		id: toolMenu;
		content: MenuLayout {

			MenuItem {
				text: "Ping Watch";
				onClicked: rootWin.ping();
			}

			MenuItem {
				text: "About";
				onClicked: rootWin.showMessage("Rockwatch", "Version: 1.0\n\nAuthor: Mike Sheldon (elleo@gnu.org)\n\nLicense: GPL 3.0 or later\n");
			}

		}
	}

	ToolBarLayout {
		id: commonTools;
		visible: true;

		Row {
			Image {
				id: backIcon
				height: 32;
				width: 32;
				fillMode: Image.PreserveAspectFit;
				smooth: true;
				visible: false;
				source: "image://theme/icon-m-toolbar-back-white";
				MouseArea {
					anchors.fill: parent;
					onClicked: {
						rootWin.back();
						rootWin.hideBack();
					}
				}
			}
		}
	}

	QueryDialog {
		id: messageDialog;
		acceptButtonText: "Okay";
	}

	QueryDialog {
		id: quitDialog;
		acceptButtonText: "Okay";
		onAccepted: {
			quit();
		}
	}
}
