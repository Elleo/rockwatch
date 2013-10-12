import QtQuick 1.1;
import Qt 4.7
import com.nokia.meego 1.0;


Page {
	id: menu;

	Image {
		id: watchImg;
		source:	"../watch.png";
		opacity: rootWin.watchOpacity;
		Behavior on opacity { PropertyAnimation { duration: 1000 } }
		anchors.centerIn: parent;
		anchors.verticalCenterOffset: -18;
		MouseArea {
			anchors.fill: parent;
			onClicked: {
				if(!rootWin.working) {
					toolMenu.open();
				}
			}
		}
	}
	
	Menu {
		id: toolMenu;
		content: MenuLayout {

			MenuItem {
				text: "Ping watch";
				onClicked: rootWin.ping();
			}

			MenuItem {
				text: "Install app or watchface";
				onClicked: {
					rootWin.openFile("WatchfaceSelector.qml");
				}
			}

			MenuItem {
				text: "Delete apps";
				onClicked: {
					rootWin.getAppList();
					rootWin.openFile("DeleteApp.qml");
				}
			}

			MenuItem {
				text: "Set watch time from phone";
				onClicked: {
					rootWin.setTime();
				}
			}

			MenuItem {
				text: "Check for firmware update"
				onClicked: {
					rootWin.firmwareCheck();
				}
			}

			MenuItem {
				text: "About";
				onClicked: rootWin.showMessage("Rockwatch", "Version: 1.1\n\nAuthor: Mike Sheldon (elleo@gnu.org)\n\nLicense: GPL 3.0 or later\n");
			}

		}
	}
}
