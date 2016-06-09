(function () {
  var
    rmultiDash = /([A-Z])/g,
    rclass = /[\t\r\n\f]/g,
    trim = "".trim,
    rtrim = /^[\s\uFEFF\xA0]+|[\s\uFEFF\xA0]+$/g,
    globalToken = [],
    all = [],
    mapID = {},
    mapCandidateID = {},
    handlers = function (param) {
      if (typeof param === "string") {
        if (mapID[param] >= 0) {
          return all[mapID[param]];
        } else if (mapCandidateID[param]) {
          mapID[param] = all.length;

          globalToken.push(mapCandidateID[param].token);
          all.push(mapCandidateID[param].hanlder);

          delete mapCandidateID[param];

          return all[mapID[param]];
        }
      } else {
        return new handlers.fn.init(param);
      }
    },
    getText = function (elem) {
      var node,
        ret = "",
        nodeType = elem.nodeType;

      if (nodeType === 1 || nodeType === 9 || nodeType === 11) {
        if (typeof elem.textContent === "string") {
          return elem.textContent;
        } else {
          for (elem = elem.firstChild; elem; elem = elem.nextSibling) {
            ret += getText(elem);
          }
        }
      } else if (nodeType === 3 || nodeType === 4) {
        return elem.nodeValue;
      }
      // Do not include comment or processing instruction nodes

      return ret;
    };

  function sibling(cur, dir) {
    if (!cur) return;

    do {
      cur = cur[dir];
    } while (cur && cur.nodeType !== 1);

    return cur;
  }

  handlers.fn = handlers.prototype = {
    init: function (obj) {
      var token = {};

      var o = this.handler || new obj(this, token),
        $elem = o.args && $(o.args[0]),
        $context;

      if ($elem && $elem[0] && ($context = $elem.closest(o.args[1]))[0]) {
        o.jcontext = $context;

        if (o.init) {
          o.init($context);
        }

        globalToken.push(token);

        if (o.args[3]) {
          mapID[o.args[3]] = all.length;
        }

        all.push(o);

        // store all handler that has an ID for the later init
      } else if (o.args && o.args[3]) {
        mapCandidateID[o.args[3]] = {
          hanlder: o,
          token: token
        };
      }

      this["handler"] = o;
      return this;
    },
    extend: function (obj) {
      if (typeof obj !== "object") return obj;
      var source, prop;
      for (var i = 1, length = arguments.length; i < length; i++) {
        source = arguments[i];
        for (prop in source) {
          if (hasOwnProperty.call(source, prop)) {
            obj[prop] = source[prop];
          }
        }
      }
      return obj;
    },
    loop: function (parent, fn, dir) {
      if (!parent) return;

      var n = dir ? parent.lastChild : parent.firstChild,
        sib = dir ? "previousSibling" : "nextSibling",
        i = 0;

      for (; n; n = n[sib]) {
        if (n.nodeType === 1 && fn.call(parent, n, i++)) {
          return;
        }
      }
    },
    isWindow: function (obj) {
      return obj !== null && obj == obj.window;
    },
    offset: function (elem) {
      var box = {
          top: 0,
          left: 0
        },
        docElem = document.documentElement;

      if (elem.getBoundingClientRect) {
        box = elem.getBoundingClientRect();
      }

      return {
        top: box.top + (window.pageYOffset || docElem.scrollTop) - (docElem.clientTop || 0),
        left: box.left + (window.pageXOffset || docElem.scrollLeft) - (docElem.clientLeft || 0)
      };
    },
    next: function (elem) {
      return sibling(elem, "nextSibling");
    },
    prev: function (elem) {
      return sibling(elem, "previousSibling");
    },
    fstChild: function (elem) {
      var ret = elem && elem.firstChild;

      return ret ? (ret.nodeType == 1) ? ret : sibling(ret, "nextSibling") : undefined;
    },
    lstChild: function (elem) {
      var ret = elem && elem.lastChild;

      return ret ? (ret.nodeType == 1) ? ret : sibling(ret, "previousSibling") : undefined;
    },
    hasClass: function (elem, className) {
      var pattern;
      return (pattern = new RegExp("(^|[\\x20\\t\\r\\n\\f])" + className + "([\\x20\\t\\r\\n\\f]|$)")) && pattern.test(typeof elem.className === "string" && elem.className || "");
    },
    toggle: function(elem, o, n){
      return elem && elem.nodeType == 1 && (elem.className = elem.className.replace(o, n));
    },
    text: function (elem, value) {
      return value === undefined ?
        getText(elem) :
        this.empty(elem).appendChild(document.createTextNode(value));
    },
    trim: trim ?
      function (text) {
        return text == null ?
          "" :
          trim.call(text);
      } : function (text) {
        return text == null ?
          "" :
          (text + "").replace(rtrim, "");
      },
    isEmpty: function (obj) {
      var n;

      if (obj.nodeType && obj.nodeType === 1) {
        if (this.fstChild(obj)) {
          return false;
        }
      } else {
        for (n in obj) {
          return false;
        }
      }

      return true;
    },
    empty: function (elem) {
      while (elem.firstChild) {
        elem.removeChild(elem.firstChild);
      }

      return elem;
    },
    removeClass: function (elem, className) {
      var cur, finalValue;

      if (typeof className === "string" && className) {

        cur = elem.nodeType === 1 && (elem.className ?
          (" " + elem.className + " ").replace(rclass, " ") :
          ""
        );

        if (cur) {

          if (cur.indexOf(" " + className + " ") >= 0) {
            cur = cur.replace(" " + className + " ", " ");
          }

          finalValue = cur.replace(/^\s|\s$/g, "");
          if (elem.className !== finalValue) {
            elem.className = finalValue;
          }
        }
      }
    },
    data: function (elem, key) {
      var data;

      if (elem && elem.nodeType === 1) {

        var name = "data-" + key.replace(rmultiDash, "-$1").toLowerCase();

        data = elem.getAttribute(name);

        if (typeof data === "string") {
          try {
            data = data === "true" ? true :
              data === "false" ? false :
              data === "null" ? null :
              // Only convert to a number if it doesn't change the string
              +data + "" === data ? +data :
              data;
          } catch (e) {}
        } else {
          data = undefined;
        }
      }

      return data;
    },
    json: function (s) {
      return window.JSON ? window.JSON.parse(s) : eval("(" + s + ")");
    },
    addClass: function (elem, className) {
      var cur, finalValue;

      if (typeof className === "string" && className) {

        cur = elem.nodeType === 1 && (elem.className ?
          (" " + elem.className + " ").replace(rclass, " ") :
          " "
        );

        if (cur) {

          if (cur.indexOf(" " + className + " ") < 0) {
            cur += className + " ";
          }

          finalValue = cur.replace(/^\s|\s$/g, "");
          if (elem.className !== finalValue) {
            elem.className = finalValue;
          }
        }
      }
    },
    getData: function (obj, async, fn) {
      var ret,
        as = async || false;

      $.ajax({
        type: 'POST',
        url: obj.url,
        data: obj.data,
        cache: false,
        async: as,
        success: function (data) {
          if (data && !as) {
            ret = data;
          } else {
            fn(data);
          }
        },
        error: function () {
          console.log('An error occured. Please try again!');
        }
      });

      return ret;
    }
  };

  handlers.fn.init.prototype = handlers.fn;

  function onLanding(event) {
    var $this, context, handler, args,
      $that = $(event.target),
      i = all.length,
      free = true,
      interval, token;

    while (i--) {
      handler = all[i];
      token = globalToken[i];

      if (handler.args) {
        $this = $that.closest((args = handler.args)[0]);
        context = $this.closest(args[1])[0];

        if (context) {
          free = false;
          interval = handler.timer ? handler.timer(context) : 0;

          if (token.elem) {
            // return soon if still inside main context
            if (token.elem === $this[0]) {
              continue;
            }
            // else still inside outer context but diffence main context
            else {

              landingHandler.call(null, null, $that, "", null, interval, token);
            }
          }

          landingHandler.call(context, $this, $that, args[2], handler.fn, interval, token);
        } else if (token.context) {
          landingHandler.call(null, null, $that, "", null, 0, token);
        }
      }
    }
  }

  function diff(root, curClass, className) {
    var rold = new RegExp(root + "\\s([\\w-\\s]+)$"),
      match, ret = curClass ? curClass : root;

    if ((match = rold.exec(className))) {
      ret += " " + match[1];
    }

    return ret;
  }

  function landingHandler(elem, target, className, fn, timer, globalToken) {
    var backupClass, done,
      _context = this,
      _this = elem && elem[0],
      old = globalToken.elem || undefined;

    if (globalToken.timer) {
      clearTimeout(globalToken.timer);
      globalToken.timer = null;
    }

    if (timer) {
      globalToken.timer = setTimeout(function () {
        landingHandler.call(_context, elem, target, className, fn, 0, globalToken);
      }, timer);

      return;
    }

    if (old) {

      if (old === _this) {
        return;

        // still inside context but different elem
      } else if (old !== _this) {
        if (globalToken.fn) {
          done = globalToken.fn.call(_context, target);
        }

        if (done) {

          old.className = globalToken.backupClass;

        }
      }

      if (done || !globalToken.fn) {
        cleanObject(globalToken);
      }
    }

    if (handlers.fn.isWindow(_context)) {

      return;
    }

    backupClass = _this.className;
    globalToken.elem = _this;
    globalToken.context = _context;
    globalToken.backupClass = backupClass;

    if (fn) {
      globalToken.fn = fn.call(_context, elem, _this);
    }

    if (className && typeof className === "string") {
      _this.className += " " + className;
    }
  }

  function cleanObject(obj) {

    for (var p in obj) {

      if (p == "length") {
        obj[p] = 0;
        continue;
      }

      try {
        delete obj[p];
      } catch (e) {
        return obj;
      }
    }
    obj = null;

    return obj;
  }

  $(document).on('mouseover', onLanding);

  window.handlers = handlers;
})();

$(function(){
  
  
// tab
handlers(function (fn, token) {
  var
  ri = /_tab-(\d+)/,
  doTab = function(e){
    var that = e.target,
        tab = this, 
        container = tab.parentNode.parentNode,
        tabber = tabbers[tab.parentNode[ex]],
        ti;
    
    if( ti = this.className.match(ri)) {
      if( fn.hasClass(container, "stick") ) {
        fn.removeClass(container, "show");  
      }
      
      fn.loop(container, function(elem, index) {
        var ci;
        if( tabber.h !== tab && (ci = elem.className.match(ri)) && ci[1] == ti[1] ) {
          elem.className += " show";
          token.backupClass = tab.className += " selected";
          fn.removeClass(tabber.h, "selected");
          fn.removeClass(tabber.c, "show");
          tabber.h = tab;
          tabber.c = elem;
          return 1;
        }
      });
    } else if( $(that).closest(".toggle")[0] ) {
      if( fn.hasClass(container, "stick") ) {
        fn.removeClass(container, "stick");
        fn.removeClass(container, "show");
      } else {
        container.className += " stick show";
      }
    }
  },
  hideStick = function(e){
    if( !head || $(e.target).closest(".tab-content")[0]) return;
    if( !t && fn.hasClass(head, "stick") && !fn.hasClass(head, "show") ) head.className += " show";
  },
  head = document.getElementById("mapHead"),
  ex = "htab",
  tabbers = {}, t;

  this.init = function (ct) {
    var i = ct.length, cur, tabber;
    
    while( i-- ) {
      cur = ct[i];
      cur[ex] = i;
      tabber = tabbers[i] = {};
      
      // find and store the actived elem
      fn.loop(cur, function(elem, index){
        if( fn.hasClass(elem, "selected") ) {
          tabber["h"] = elem;
          fn.loop(elem.parentNode.parentNode, function(elem, index){
            if(fn.hasClass(elem, "show")){
              tabber["c"] = elem;
              return 1;
            }
          });
          return 1;
        }
      });
    }
    
    $(document).on("click", hideStick);
  };

  this.args = ["._tab", "._htab", ""];

  this.fn = function (elem, _elem) {
    t = _elem;
    elem.on("click", doTab);
    return function () {
      elem.off("click", doTab);
      t = null;
      return true;
    };
  };

  return this;
});
  
// popup
handlers(function (fn, token) {
  var showPop = function(e){
    var target = document.getElementById(this.getAttribute("data-target"));
    if( !target ) return;
    if( !fn.hasClass(target, "show") ) {
      target.className += " show";
      curShow = target;
      !stack.length && stack.push("");
      stack.push(function(){
        fn.removeClass(target, "show");
      });
    } else clear(e);
    e.preventDefault();
  },
  clear = function(e){
    var $that = $(e.target), fn;
    if( $that.closest(curShow)[0] ) return;
    fn = stack.shift()
    fn && fn();
  }, stack = [], curShow;
  
  this.args = ["._hpop", "._hpop"];

  this.fn = function (elem, _elem) {
    elem.on("click", showPop);
    return function () {
      elem.off("click", showPop);
      return true;
    };
  };
  
  $(document).on("click", clear);
  
  return this;
});
  
// layer group
handlers(function (fn, token) {
  var 
  rt = /fa-(?:un)?(\w+)/,
  layer = function(){
    var m;
    (m = this.className.match(rt)) && kits[m[1]].call(this);
  },
  kits = {
    eye: function(){
      var o = "fa-eye", n = "fa-eye-slash";
      !fn.hasClass(this, o) && (o = n, n = "fa-eye");
      change(this, o, n);
    },
    folder: function(){
      var g = $g[0];
      !fn.hasClass(g, "open") ? (g.className += " open") : fn.removeClass(g, "open");
    },
    lock: function(){
      var o = "fa-lock", n = "fa-unlock";
      !fn.hasClass(this, o) && (o = n, n = "fa-lock");
      change(this, o, n);
    },
    info: function(){
      var o = "fa-info", n = "fa-info-circle";
      !fn.hasClass(this, o) && (o = n, n = "fa-info");
      change(this, o, n);
    }
  },
  change = function(node, o, n){
    token.backupClass = fn.toggle(node, o, n);
      
    fn.hasClass(node, "__root") && $g.find("." + o).each(function(index, elem) {
      fn.toggle(elem, o, n);
    });
  }, $g;
  
  this.args = ["._lt", ".layer"];

  this.fn = function (elem, _elem) {
    $g = $(this).closest(".layer-group");
    elem.on("click", layer);
    return function () {
      elem.off("click", layer);
      return true;
    };
  };

  return this;
});
  
(function(fn){
  var siteHeader = document.getElementById("siteHeader"),
      shrinked = 0;
  
  if( !siteHeader ) return;
  
  $(window).on("scroll", function(){
    var top = (window.pageYOffset || document.documentElement.scrollTop);

    if( !shrinked && top > 24 ) {
      siteHeader.className += " shrink";
      shrinked = 1;
    } else if( top < 24 ) {
      shrinked = 0;
      fn.removeClass(siteHeader, "shrink");
    }
  }); 
})(handlers.fn);
  
(function(fn){
  var change = function(e){
    var $container = $(this).closest(".graph-container"),
        that = e.target,
        $li = $(that), li, tg, tgs, view, i;
    
    if( !(li = $li.closest("li")[0]) ) {
      return;
    }
    
    if( tg = fn.data(li, "target") ) {
      view = document.getElementById(tg);
      $container.find(".view").removeClass("view");
      $container.find(".selected").removeClass("selected");
      view && (view.className += " view");
      
      tgs = targets[tg];
      i = tgs.length;
      while( i-- ) {
        tgs[i].className += " selected";
      }
    }
    
    e.preventDefault();
  },
  $sts = $(".statistic"),
  targets = {};
  
  $sts.each(function(index, elem){
    fn.loop(this, function(elem, index){
      var t = fn.data(elem, "target"),
          cur;
      if( t ) {
        cur = targets[t] || (targets[t] = []);
        cur.push(elem);
      }
    });
  });
  
  $sts.on("click", change);
})(handlers.fn); 

(function(fn) {
  window.pop = function(id){
    var show = document.getElementById(id);
    show && fn.hasClass(show, "show") ? fn.removeClass(show, "show") : (show.className += " show");
  }
})(handlers.fn);
  
}); // end jq

