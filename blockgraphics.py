# -*- coding: utf-8 -*-

pipes = {
        (True , 
   True ,      True , 
         True ) : '╬',

        (True , 
   True ,      True , 
         False) : '╩',

        (False, 
   True ,      True , 
         True ) : '╦',

        (False, 
   True ,      True , 
         False) : '═',

        (True , 
   True ,      False, 
         True ) : '╣',

        (True , 
   True ,      False, 
         False) : '╝',

        (False, 
   True ,      False, 
         True ) : '╗',

        (False, 
   True ,      False, 
         False) : '╡',

        (True , 
   False,      True , 
         True ) : '╠',

        (True , 
   False,      True , 
         False) : '╚',

        (False, 
   False,      True , 
         True ) : '╔',

        (False, 
   False,      True , 
         False) : '╞',

        (True , 
   False,      False, 
         True ) : '║',

        (True , 
   False,      False, 
         False) : '╨',

        (False, 
   False,      False, 
         True ) : '╥',

        (False, 
   False,      False, 
         False) : '═',

  }

blocks = {
    ( True , True ,
      True , True ) : '█',

    ( True , True ,
      True , False) : '▛',

    ( True , True ,
      False, True ) : '▜',

    ( True , True ,
      False, False) : '▀',

    ( True , False,
      True , True ) : '▙',

    ( True , False,
      True , False) : '▌',

    ( True , False,
      False, True ) : '▚',

    ( True , False,
      False, False) : '▘',

    ( False, True ,
      True , True ) : '▟',

    ( False, True ,
      True , False) : '▞',

    ( False, True ,
      False, True ) : '▐',

    ( False, True ,
      False, False) : '▝',

    ( False, False,
      True , True ) : '▄',

    ( False, False,
      True , False) : '▖',

    ( False, False,
      False, True ) : '▗',

    ( False, False,
      False, False) : ' ',

  }
