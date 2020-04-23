'''
GNU V2, Denis Kim 2020, deniskim2@me.com

Featured class for holding dict.

Features:
- access to dict values same as attributes (ex. dict['key'] == dict.key)
- default values
- selection prefixes for keys separately for each caller module
- load value with conversion from string according type of default value
- value change history
- available some standart dict methods:
    keys(), update(), get(), setdefault(), del ...
'''
import inspect

class Data:
    '''
        Methods:
        --------
        .use(<key>, <value>)
            set default value wich used for:
            - retrive value while other value not assigned
            - define type conversion for string parsing

        .clear(<key>)
            clear value. Will available default value

        .parse(<key>, <str>)
            parsing string with type conversion according with
            type of default value

        .update(<data>)
            updating items and values from other <class Data> or <class dict>

        .select(<prefix>, end='_', isGlobal=False)
            setting default prefix for caller module or all modules
            when prefix is defined for finding key using options:
                in first, key = <prefix> + <end> + <key>
                in second, key = <key>

            when isGlobal=False, selected prefix used only for call
            from current module. For each module used different prefix

            when isGloval=True, selected prefix used for all calls
            independent of caller module

            example:
                d = Data()
                d.a = 1; d.b=2; d.loc_a = 3
                d.select('loc')
                d.a
                    => 3
                d.b
                    => 2

        Attributes:
        -----------
        .history - историz чтения и записи атрибутов
                   в виде [<модуль>.<функция>, <новое значение>]
                        начать запись:     .history['key']=[]
                        остановить запись: del .history['key']
                        посмотреть историю: .history['key']
    '''
    def __init__(self):
        self.__dict__['items'] = {}      # Текущие значения
        self.__dict__['defaults'] = {}   # Значения по умолчанию и типы
        self.__dict__['assigns'] = {}    # Признак что значение было присвоено явно
        self.__dict__['history'] = {}    # история изменения значения атрибута
        self.__dict__['sources'] = {}    # источники значений
        self.__dict__['prefix'] = ''     # используемый глобальный префикс
        self.__dict__['prefixes'] = {}   # используемые префиксы для модулей

    # Определяет значение по умолчанию для атрибута
    def use(self, name, default, source=None):
        self.defaults[name] = default
        if not name in self.items: self.items[name] = None
        if not name in self.assigns: self.assigns[name] = None
        if not name in self.sources: self.sources[name] = source

    # Очищает один элемент
    def clear(self, name):
        self.items[name] = None
        self.assigns[name] = None
        self.add_history(name, caller='.clear')

    # Устанавливает значение атрибута из строки по типу соотв. defaults
    def parse(self, key, valueStr):
        varType = type(self.defaults[key])
        if varType == int: self.items[key] = int(valueStr)
        elif varType == float: self.items[key] = float(valueStr)
        else: self.items[key] = valueStr

    # Дополняет словарь из другого экземпляра Data или dict
    def update(self, data):
        if type(data) == type(self):
            self.items.update(data.items)
            self.defaults.update(data.defaults)
            self.assigns.update(data.assigns)
            self.history.update(data.history)
            self.sources.update(data.sources)
        elif type(data) == dict:
            self.items.update(data.items)

            for k,v in data.items():
                # Добавляем в assigns все ключи из нового набора
                # что бы их правильно обрабатывал getitem
                if k not in self.asigns: self.asigns[k] = '.update'

                # Обновляем историю по отслеживаемым элементам
                if k in self.history: self.history.append(['.update', v])

        return self

    # Устанавливает текущий префикс
    def select(self, prefix='', end='_', isGlobal=False):
        if isGlobal:
            # Меняем глобальный префикс
            if prefix!='' and end and type(end)==str:
                self.__dict__['prefix'] = prefix + end

            else:
                self.__dict__['prefix'] = prefix
        else:
            module = self.get_caller_module()
            if prefix!='' and end and type(end)==str:
                self.__dict__['prefixes'][module] = prefix + end
            else:
                self.__dict__['prefixes'][module] = prefix


    def get_caller_module(self):
        frames = inspect.getouterframes(inspect.currentframe())[1:]
        for f in frames:
            module = f.filename.split('/')[-1]
            if module != 'i_data.py':
                return module


    def get_caller(self, idx=2):
        frames = inspect.getouterframes(inspect.currentframe())[1:]
        for f in frames:
            module = f.filename.split('/')[-1]
            if module != 'i_data.py':
                return module + '.' +f.function


    def get_prefix(self):
        if len(self.__dict__['prefix']): return self.__dict__['prefix']

        module = self.get_caller_module()
        prefix = self.__dict__['prefixes'].get(module,'')
        return prefix

    # Возвращает префиксы для которых определен атрибут
    def find_prefix(self, key, end='_'):
        prefixes = []
        if key in self.items: prefixes.append('')

        for k in self.items.keys():
            if k.endswith(end+key):
                prefixes.append(k[:-len(end+key)])

        return prefixes

    # Определяет полное имя ключа - с префиксом или без
    def find_key(self, key):
        prefixKey = self.get_prefix() + key
        if prefixKey in self.__dict__['items'].keys():
            return prefixKey
        if key in self.__dict__['items'].keys():
            return key
        else:
            return None


    def keys(self):
        if self.prefix=='':
            return self.items.keys()
        else:
            return [key for key in self.items.keys() if key.startswith(self.prefix)]


    def get(self, key, default=None):
        return self.items.get(key, default)


    def setdefault(self, key, default):
        if key not in self.__dict__['items'].keys():
            self.items[key] = default
        return self.items[key]


    def __getattr__(self, name):
        '''Если атрибут обновлялся (.assigns[key])
           возвращаем его значение (.items[key])
           иначе возвращаем значение из .defaults[key]
        '''
        name = self.find_key(name)
        assert(name)

        self.add_history(name)
        if self.__dict__['assigns'].get(name):
            return self.__dict__['items'][name]
        else:
            value = self.__dict__['defaults'][name]
            if value:
                return value
            else:
                raise Exception('Неизвестный атрибут '+name)


    def __getitem__(self, key):
        self.add_history(key)
        return self.__getattr__(key)


    def __setitem__(self, key, value):
        self.items[key] = value
        if self.defaults.get(key)==None: self.defaults[key] = None
        self.add_history(key, value)


    def __setattr__(self, name, value):
        self.__setitem__(name, value)


    def __delitem__(self, key):
        if key in self.items: del self.items[key]
        if key in self.defaults: del self.defaults[key]
        if key in self.assigns: del self.assigns[key]


    def __delattr__(self, key):
        self.__delitem__(key)


    def __repr__(self):
        return str(self.items)


    def add_history(self, key, value=None, caller=None):
        if not caller: caller = self.get_caller(idx=3)
        if value!=None: self.assigns[key] = caller
        if key in self.history:
            self.__dict__['history'][key].append( [caller, value] )
