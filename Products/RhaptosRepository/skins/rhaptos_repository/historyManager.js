// from http://unfocus-history-keeper.googlecode.com/svn/
// http://unfocus-history-keeper.googlecode.com/svn/tags/Release_2.0b2/javascript/EventManager.js
// http://unfocus-history-keeper.googlecode.com/svn/tags/Release_2.0b2/javascript/History.js

/*
unFocus.EventManager, version 1.0 (2007/09/11)
Copyright: 2005-2007, Kevin Newman (http://www.unfocus.com/Projects/)

This file is part of unFocus.History Keeper.

unFocus.History Keeper is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation; either version 3 of the License, or (at your option) any later version.

unFocus.History Keeper is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/
// Package: unFocus.Utilities
// make sure faux-namespace is available before adding to it
if (!window.unFocus) var unFocus = {};

/** Class: EventManager
 *	Provides the interface and functionality to a Subscriber/Subscriber Pattern.
 * 
 **/
/*
Constructor: EventManager
	The Constructor (Prototype) function.

Parameters:
	[type1 [, type2 [, etc.]]] - Optionally sets up an empty array for each named event.
*/
unFocus.EventManager = function() {
	this._listeners = {};
	for (var i = 0; i < arguments.length; i++) {
		this._listeners[arguments[i]] = [];
	}
};

unFocus.EventManager.prototype = {
	/*
	Method: addEventListener
		Adds an event listener to the specified type.

	Parameters:
		$name		- The event name.
		$listener	- The function to be called when the event fires.
	*/
	addEventListener: function($name, $listener) {
		// check that listener is not in list
		for (var i = 0; i < this._listeners[$name].length; i++)
			if (this._listeners[$name][i] == $listener) return;
		// add listener to appropriate list
		this._listeners[$name].push($listener);
	},
	/*
	Method: removeEventListener
		Removes an event listener.
	
	Parameters:
		$name		- The event name.
		$listener	- The function to be removed.
	*/
	removeEventListener: function($name, $listener) {
		// search for the listener method
		for (var i = 0; i < this._listeners[$name].length; i++) {
			if (this._listeners[$name][i] == $listener) {
				this._listeners.splice(i,1);
				return;
			}
		}
	},
	/* Method: notifyListeners
		Notifies the listeners of an event.
	
	Parameters:
		$name	- The name of event to fire.
		$data	- The object to pass to the subscribed method (the Event Object).
	*/
	notifyListeners: function($name, $data) {
		for (var i = 0; i < this._listeners[$name].length; i++)
			this._listeners[$name][i]($data);
	}
};


/*
unFocus.History, version 2.0 (beta 1) (2007/09/11)
Copyright: 2005-2007, Kevin Newman (http://www.unfocus.com/Projects/)

This file is part of unFocus.History Keeper.

unFocus.History Keeper is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation; either version 3 of the License, or (at your option) any later version.

unFocus.History Keeper is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

/*
	Class: unFocus.History
		A singleton with subscriber interface (<unFocus.EventManager>) 
		that keeps a history and provides deep links for Flash and AJAX apps
*/
unFocus.History = (function() {

// use a closure to avoid poluting the global scope, and to discourage reinstantiation (like a singleton)
function Keeper() {
	// bool: initialize - whether or not the class has been initialized
	var _this = this,
		// set the poll interval here.
		_pollInterval = 200, _intervalID,
		// get the initial Hash state
		_currentHash;

	/*
	method: _getHash
		A private method that gets the Hash from the location.hash property.
	 
	returns:
		a string containing the current hash from the url
	*/
	var _getHash = function() {
		return location.hash.substring(1);
	};
	// get initial hash
	_currentHash = _getHash();
	
	/*
	method: _setHash
		A private method that sets the Hash on the location string (the current url).
	*/
	var _setHash = function($newHash) {
		window.location.hash = $newHash;
	};
	
	/*
	method: _watchHash
		A private method that is called every n miliseconds (<_pollInterval>) to check if the hash has changed.
		This is the primary Hash change detection method for most browsers. It doesn't work to detect the hash
		change in IE 5.5+ or various other browsers. Workarounds like the iframe method are used for those 
		browsers (IE 5.0 will use an anchor creation hack).
	*/
	function _watchHash() {
		var $newHash = _getHash();
		if (_currentHash != $newHash) {
			_currentHash = $newHash;
			_this.notifyListeners("historyChange", $newHash);
		}
	}
	// set the interval
	if (setInterval) _intervalID = setInterval(_watchHash, _pollInterval);
	
	/* 
	Method: _createAnchor
		Various browsers may need an achor to be present in the dom for the hash to actually be set,
		so we add one every time a history entry is made. This has a side effect in many browsers, 
		where if the scroll position of the page is changed, in between history states, this causes
		most browsers to remember the position! It's a bonus.
	*/
	function _createAnchor($newHash) {
		if (!_checkAnchorExists($newHash)) {
			var $anchor;
			if (/MSIE/.test(navigator.userAgent) && !window.opera)
				$anchor = document.createElement('<a name="'+$newHash+'">'+$newHash+"</a>");
			else
				$anchor = document.createElement("a");
			$anchor.setAttribute("name", $newHash);
			with ($anchor.style) {
				position = "absolute";
				display = "block";
				top = getScrollY()+"px";
				left = getScrollX()+"px";
			}
			//$anchor.style.display = 'none';
			//$anchor.innerHTML = $newHash;
			document.body.insertBefore($anchor,document.body.firstChild);
			//document.body.appendChild($anchor);
		}
	}
	// simplified function contributed by Micah Goulart
	function _checkAnchorExists($name) {
		if (document.getElementsByName($name).length > 0)
			return true;
	}
	// Keeps IE 5.0 from scrolling to the top every time a new history is entered.
	// Also retains the scroll position in the history (doesn't seem to work on IE 5.5+).
	if (typeof self.pageYOffset == "number") {
		function getScrollY() {
			return self.pageYOffset;
		}
	} else if (document.documentElement && document.documentElement.scrollTop) {
		function getScrollY() {
			return document.documentElement.scrollTop;
		}
	} else if (document.body) {
		function getScrollY() {
			return document.body.scrollTop;
		}
	}
	// clone getScrollY to getScrollX
	eval(String(getScrollY).toString().replace(/Top/g,"Left").replace(/Y/g,"X"));
	
	/*
	method: getCurrentBookmark
		A public method to retrieve the current history string
	
	returns:
		The current History Hash
	*/
	_this.getCurrent = function() {
		return _currentHash;
	};
	
	/*
	method: addHistory
		A public method to add a new history, and set the deep link. This method should be given a string.
		It does no serialization.
	
	returns:
		Boolean - true if supported and set, false if not
	*/
	function addHistory($newHash) {
		if (_currentHash != $newHash) {
			_createAnchor($newHash);
			_currentHash = $newHash;
			_setHash($newHash);
			_this.notifyListeners("historyChange",$newHash);
		}
		return true;
	}
	_this.addHistory = function($newHash) { // adds history and bookmark hash
		_createAnchor(_currentHash);
		// replace with slimmer versions...
		_this.addHistory = addHistory;
		// ...do first call
		return _this.addHistory($newHash);
	};

	/**
	 * These are the platform specific override methods. Since some platforms (IE 5.5+, Safari)
	 * require almost completely different techniques to create history entries, browser detection is
	 * used and the appropriate method is created. The bugs these fixes address are very tied to the
	 * specific implementations of these browsers, and not necessarily the underlying html engines.
	 * Sometimes, bugs related to history management can be tied even to a specific skin in browsers
	 * like Opera.
	 */
	// Safari 2.04 and less (and WebKit less than 420 - these hacks are not needed by the most recent nightlies)
	// :TODO: consider whether this aught to check for Safari or WebKit - is this a safar problem, or a does it
	// happen in other WebKit based software? OmniWeb (WebKit 420+) seems to work, though there's a sync issue.
	if (/WebKit\/\d+/.test(navigator.appVersion) && navigator.appVersion.match(/WebKit\/(\d+)/)[1] < 420) {
		// this will hold the old history states, since they can't be reliably taken from the location object
		var _unFocusHistoryLength = history.length,
			_historyStates = {}, _form,
			_recentlyAdded = false;
		
		// Setting the hash directly in Safari seems to cause odd content refresh behavior.
		// We'll use a form to submit to a #hash location instead. I'm assuming this works,
		// since I saw it done this way in SwfAddress (gotta give credit where credit it due ;-) ).
		function _createSafariSetHashForm() {
			_form = document.createElement("form");
			_form.id = "unFocusHistoryForm";
			_form.method = "get";
			document.body.insertBefore(_form,document.body.firstChild);
		}
		
		// override the old _setHash method to use the new form
		_setHash = function($newHash) {
			_historyStates[_unFocusHistoryLength] = $newHash;
			_form.action = "#" + _getHash();
			_form.submit();
		};
		
		// override the old _getHash method, since Safari doesn't update location.hash (fixed in nightlies)
		_getHash = function() {
			return _historyStates[_unFocusHistoryLength];
		};
		
		// set initial history entry
		_historyStates[_unFocusHistoryLength] = _currentHash;
		
		function addHistorySafari($newHash) {
			if (_currentHash != $newHash) {
				_createAnchor($newHash);
				_currentHash = $newHash;
				_unFocusHistoryLength = history.length+1;
				_recentlyAdded = true;
				_setHash($newHash);
				_this.notifyListeners("historyChange",$newHash);
				_recentlyAdded = false;
			}
			return true;
		}
		
		// provide alternative addHistory
		_this.addHistory = function($newHash) { // adds history and bookmark hash
			// on first call, make an anchor for the root history entry
			_createAnchor(_currentHash);
			// setup the form fix
			_createSafariSetHashForm();
			
			// replace with slimmer version...
			// :TODO: rethink this - it's adding an extra scope to the chain, which might
			// actually cost more at runtime than a simple if statement. Can this be done
			// without adding to the scope chain? The replaced scope holds no values. Does
			// it keep it's place in the scope chain?
			_this.addHistory = addHistorySafari;
			
			// ...do first call
			return _this.addHistory($newHash);
		};
		function _watchHistoryLength() {
			if (!_recentlyAdded) {
				var _historyLength = history.length;
				if (_historyLength != _unFocusHistoryLength) {
					_unFocusHistoryLength = _historyLength;
					
					var $newHash = _getHash();
					if (_currentHash != $newHash) {
						_currentHash = $newHash;
						_this.notifyListeners("historyChange", $newHash);
					}
				}
			}
		};
		
		// since it doesn't work, might as well cancel the location.hash check
		clearInterval(_intervalID);
		// watch the history.length prop for changes instead
		_intervalID = setInterval(_watchHistoryLength, _pollInterval);
		
	// IE 5.5+ Windows
	} else if (typeof ActiveXObject != "undefined" && window.print &&
			   !window.opera && navigator.userAgent.match(/MSIE (\d+\.\d+)/)[1] >= 5.5) {
		/* iframe references */
		var _historyFrameObj, _historyFrameRef;
		
		/*
		method: _createHistoryFrame
			
			This is for IE only for now.
		*/
		function _createHistoryFrame() {
			var $historyFrameName = "unFocusHistoryFrame";
			_historyFrameObj = document.createElement("iframe");
			_historyFrameObj.setAttribute("name", $historyFrameName);
			_historyFrameObj.setAttribute("id", $historyFrameName);
			// :NOTE: _Very_ experimental
			_historyFrameObj.setAttribute("src", 'javascript:;');
			_historyFrameObj.style.position = "absolute";
			_historyFrameObj.style.top = "-900px";
			document.body.insertBefore(_historyFrameObj,document.body.firstChild);
			// get reference to the frame from frames array (needed for document.open)
			// :NOTE: there might be an issue with this according to quirksmode.org
			// http://www.quirksmode.org/js/iframe.html
			_historyFrameRef = frames[$historyFrameName];
			
			// add base history entry
			_createHistoryHTML(_currentHash, true);
		}
		
		/*
		method: _createHistoryHTML
			This is an alternative to <_setHistoryHTML> that is used by IE (and others if I can get it to work).
			This method will create the history page completely in memory, with no need to download a new file
			from the server.
		*/
		function _createHistoryHTML($newHash) {
			with (_historyFrameRef.document) {
				open("text/html");
				write("<html><head></head><body onl",
					'oad="parent.unFocus.History._updateFromHistory(\''+$newHash+'\');">',
					$newHash+"</body></html>");
				close();
			}
		}
		
		/*
		method: _updateFromHistory
			A private method that is meant to be called only from HistoryFrame.html.
			It is not meant to be used by an end user even though it is accessable as public.
		*/
			// hides the first call to the method, and sets up the real method for the rest of the calls
		function updateFromHistory($hash) {
			_currentHash = $hash;
			_this.notifyListeners("historyChange", $hash);
		}
		_this._updateFromHistory = function() {
			_this._updateFromHistory = updateFromHistory;
		};
		//if (navigator.userAgent.match(/MSIE (\d\.\d)/)[1] < 5.5) {
			function addHistoryIE($newHash) { // adds history and bookmark hash
				if (_currentHash != $newHash) {
					// IE will create an entry if there is an achor on the page, but it
					// does not allow you to detect the state change, so we skip inserting an Anchor
					_currentHash = $newHash;
					// sets hash and notifies listeners
					_createHistoryHTML($newHash);
				}
				return true;
			};
			_this.addHistory = function($newHash) {
				// do initialization stuff on first call
				_createHistoryFrame();
				
				// replace this function with a slimmer one on first call
				_this.addHistory = addHistoryIE;
				// call the first call
				return _this.addHistory($newHash);
			};
			// anonymouse method - subscribe to self to update the hash when the history is updated
			_this.addEventListener("historyChange", function($hash) { _setHash($hash) });
		//} else { /* IE 5.0 */ }
	
	}
}
Keeper.prototype = new unFocus.EventManager("historyChange");

return new Keeper();

})();

