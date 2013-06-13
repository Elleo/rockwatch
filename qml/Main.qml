import QtQuick 1.1;
import Qt 4.7
import com.nokia.meego 1.0;

PageStackWindow {
	id: rootWin;
	property int pageMargin: 16;
	property double watchOpacity: 0.25;
	property bool working: false;

	Component.onCompleted: {
		theme.inverted = true;
	}

	signal watchfaceSelected(string url);
	signal firmwareCheck();
	signal upgradeFirmware();
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
		rootWin.working = true;
	}

	function stopWorking() {
		indicator.running = false;
		indicator.opacity = 0;
		rootWin.working = false;
	}

	function connected() {
		rootWin.watchOpacity = 1;
	}

	function newFirmwareAvailable(oldVersion, newVersion) {
		firmwareDialog.message = "Old version: " + oldVersion +"\nNew version: " + newVersion + "\n\nWould you like to upgrade now?";
		firmwareDialog.open();
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

	BusyIndicator {
		id: indicator
		platformStyle: BusyIndicatorStyle { size: "large" }
		running:  false;
		Behavior on opacity { PropertyAnimation { duration: 100 } }
		opacity: 0;
		anchors.centerIn: parent;
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

	QueryDialog {
		id: firmwareDialog;
		titleText: "Firmware upgrade available";
		acceptButtonText: "Upgrade";
		rejectButtonText: "Cancel";
		onAccepted: {
			upgradeFirmware();
		}
	}
}
