import QtQuick 1.1;
import Qt.labs.components 1.0;
import com.nokia.meego 1.0;
import com.nokia.extras 1.0;

import QtMobility.gallery 1.1;

Page {
	id: watchfaceSelector;
	tools: ToolBarLayout {
		id: tools;
		ToolButton {
			width: 64;
			height: 64;
			iconSource: "image://theme/icon-m-toolbar-back-white";
			onClicked: { 
				pageStack.pop(); 
				tools.visible = false;
			}
		}
	}

	DocumentGalleryModel {
		id: watchfaceFileModel;

		rootType: DocumentGallery.File;
		properties: ["url", "fileName"];
		filter: GalleryWildcardFilter {
			property: "fileName";
			value: "*.pbw";
		}
	}

	ListView {
		anchors.fill: parent;
		model: watchfaceFileModel;
		delegate: watchfaceFileDelegate;
	}

	Component {
		id: watchfaceFileDelegate;

		Item {
			height: 60;
			width: parent.width;
			MouseArea {
				anchors.fill: parent

				Image {
					id: watchfaceIcon;
					source: "image://theme/icon-m-transfer-download";
					anchors.rightMargin: 10;
				}

				Label {
					height: parent.height;
					width: parent.width - watchfaceIcon.width;
					text: fileName;
					font.pointSize: 18;
					font.bold: true;
					anchors.left: watchfaceIcon.right;
					verticalAlignment: Text.AlignVCenter;
					elide: Text.ElideRight;
				}

				onClicked: { 
					pageStack.pop();
					console.log("Selected watchface: " + url); 
					rootWin.watchfaceSelected(url); 
				}
			}
		}
	}
}
