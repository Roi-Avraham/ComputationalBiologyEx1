from tkinter import Tk, LabelFrame, Label, Entry, Canvas, Button, messagebox
from automat import CellularAutomaton
from style import palette, fonts


def create_entry(master, default_value):
    """
    Creates a default entry with default value inserted.
    param master: the parent of the tk object.
    param default_value: default value to begin with.
    :return: an Entry object.
    """
    entry = Entry(
        master=master,
        font=fonts.regular,
        width=7,
        bg=palette.btn_bg,
        fg=palette.btn_fg,
        justify='center'
    )
    entry.insert(0, default_value)
    return entry


class App(Tk):
    """
    This class defines the behaviour of the app and its window.
    """

    def __init__(self):
        """
        App constructor - initializes the windows and its contents.
        :return: App object.
        """

        # Inherit Tkinter class and configure it.
        super().__init__()
        self.geometry('1100x830')
        self.minsize(1100, 830)
        self.maxsize(1100, 830)
        self.configure(background=palette.bg, highlightcolor=palette.fg)
        self.title('Spreading Rumours')

        def on_closing():
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                self.destroy()
                exit(0)
        self.protocol("WM_DELETE_WINDOW", on_closing)

        # Create a frame for a cellular automata, and instantiate and automata.
        self.frame = Canvas(
            bg=palette.canvas_bg,
            bd=0,
            highlightbackground=palette.canvas_outline,
            width=800,
            height=800)
        self.frame.place(relx=0.26, rely=0.025)
        self.cellular_automaton = CellularAutomaton(self)

        # Create configurations section with labels, entries and buttons.
        self.configuration = LabelFrame(
            master=self,
            bg=palette.bg,
            fg=palette.fg,
            text='Configuration',
            font=fonts.regular
        )
        self.configuration.place(relx=0.01, rely=0.015, width=265)

        Label(
            master=self.configuration,
            font=fonts.regular,
            bg=palette.bg,
            fg=palette.fg,
            text='Population density:'
        ).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.n_person = create_entry(self.configuration, '0.5')
        self.n_person.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        Label(
            master=self.configuration,
            font=fonts.regular,
            bg=palette.bg,
            fg=palette.fg,
            text='L:'
        ).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.L = create_entry(self.configuration, '2')
        self.L.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        Label(
            master=self.configuration,
            font=fonts.regular,
            bg=palette.bg,
            fg=palette.fg,
            text='S1:'
        ).grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.S1 = create_entry(self.configuration, '0.4')
        self.S1.grid(row=2, column=1, padx=5, pady=5, sticky='w')

        Label(
            master=self.configuration,
            font=fonts.regular,
            bg=palette.bg,
            fg=palette.fg,
            text='S2:'
        ).grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.S2 = create_entry(self.configuration, '0.2')
        self.S2.grid(row=3, column=1, padx=5, pady=5, sticky='w')

        Label(
            master=self.configuration,
            font=fonts.regular,
            bg=palette.bg,
            fg=palette.fg,
            text='S3:'
        ).grid(row=4, column=0, padx=5, pady=5, sticky='w')
        self.S3 = create_entry(self.configuration, '0.3')
        self.S3.grid(row=4, column=1, padx=5, pady=5, sticky='w')

        Label(
            master=self.configuration,
            font=fonts.regular,
            bg=palette.bg,
            fg=palette.fg,
            text='S4:'
        ).grid(row=5, column=0, padx=5, pady=5, sticky='w')
        self.S4 = create_entry(self.configuration, '0.1')
        self.S4.grid(row=5, column=1, padx=5, pady=5, sticky='w')

        Label(
            master=self.configuration,
            font=fonts.regular,
            bg=palette.bg,
            fg=palette.fg,
            text='Generation limit (Optional):'
        ).grid(row=7, column=0, padx=5, pady=5, sticky='w')
        self.gen_limit = create_entry(self.configuration, '')
        self.gen_limit.grid(row=7, column=1, padx=5, pady=5, sticky='w')

        self.pause_btn = Button(
            master=self,
            width=12,
            bg=palette.btn_bg,
            fg=palette.btn_fg,
            relief='groove',
            font=fonts.bold,
            text='\u23F8 Pause',
            command=self.pause_btn_action
        )
        self.pause_btn.place(relx=0.01, rely=0.745, width=125, height=40)

        self.stop_btn = Button(
            master=self,
            width=12,
            bg=palette.btn_bg,
            fg=palette.btn_fg,
            relief='groove',
            font=fonts.bold,
            text='\u23F9 Stop',
            command=self.stop_btn_action
        )
        self.stop_btn.place(relx=0.137, rely=0.745, width=125, height=40)

        self.run_btn = Button(
            master=self,
            width=27,
            bg=palette.btn_bg,
            fg=palette.btn_fg,
            relief='groove',
            font=fonts.bold,
            text='\u23F5 Start   ',
            command=self.run_btn_action
        )
        self.run_btn.place(relx=0.01, rely=0.745, width=265, height=40)

        # Create information section with labels and entries.
        self.information = LabelFrame(
            master=self,
            bg=palette.bg,
            fg=palette.fg,
            text='Information',
            font=fonts.regular
        )
        self.information.place(relx=0.01, rely=0.38, width=265)

        Label(
            master=self.information,
            font=fonts.regular,
            bg=palette.bg,
            fg=palette.fg,
            text='Generation:'
        ).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.generation = create_entry(self.information, 'n/a')
        self.generation.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        Label(
            master=self.information,
            font=fonts.regular,
            bg=palette.bg,
            fg=palette.fg,
            text='Heard the rumor:'
        ).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.h_rumor = create_entry(self.information, 'n/a')
        self.h_rumor.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        Label(
            master=self.information,
            font=fonts.regular,
            bg=palette.bg,
            fg=palette.fg,
            text='The spread distribution:'
        ).grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.distribution = create_entry(self.information, 'n/a')
        self.distribution.grid(row=2, column=1, padx=5, pady=5, sticky='w')

        # Create Legend section.
        self.legend = LabelFrame(
            master=self,
            bg=palette.bg,
            fg=palette.fg,
            text='Legend',
            font=fonts.regular
        )
        self.legend.place(relx=0.01, rely=0.585, width=265)

        Label(
            master=self.legend,
            font=fonts.regular,
            bg=palette.bg,
            fg=palette.fg,
            text=' \u2022  Orange - person.'
        ).grid(row=0, column=0, padx=5, pady=0, sticky='w')

        Label(
            master=self.legend,
            font=fonts.regular,
            bg=palette.bg,
            fg=palette.fg,
            text=' \u2022  Red - heard the rumor.'
        ).grid(row=1, column=0, padx=5, pady=0, sticky='w')

        # Credit.
        Label(
            master=self,
            font=fonts.credit,
            bg=palette.bg,
            fg=palette.fg,
            text='\u00A9 Created by Roi Avraham and Sigal Grabois'
        ).place(relx=0.006, rely=0.97)

    def get_input(self):
        """
        Get inputs from the app's entries and validates them. If at least one of
        the inputs are invalid, raise a descriptive error message. Otherwise,
        return validated input.
        :return: simulation's input -- experiment's parameters.
        """

        error_messages = []
        P, L, S1, S2, S3, S4, GL = 0, 0, 0, 0, 0, 0, 0

        try:
            L = int(self.L.get().strip())
            if L < 0:
                raise ValueError
        except ValueError:
            msg = 'L must be an positive int.'
            error_messages.append(msg)

        try:
            P = float(self.n_person.get().strip())
            if P < 0 or P > 1:
                raise ValueError
        except ValueError:
            msg = 'Population density must be a float between 0 and 1.'
            error_messages.append(msg)

        try:
            S1 = float(self.S1.get().strip())
            if S1 < 0 or S1 > 1:
                raise ValueError
        except ValueError:
            msg = 'S1 must be a float between 0 and 1.'
            error_messages.append(msg)

        try:
            S2 = float(self.S2.get().strip())
            if S2 < 0 or S2 > 1:
                raise ValueError
        except ValueError:
            msg = 'S2 must be a float between 0 and 1.'
            error_messages.append(msg)

        try:
            S3 = float(self.S3.get().strip())
            if S3 < 0 or S3 > 1:
                raise ValueError
        except ValueError:
            msg = 'S3 must be a float between 0 and 1.'
            error_messages.append(msg)

        try:
            S4 = float(self.S4.get().strip())
            if S4 < 0 or S4 > 1:
                raise ValueError
        except ValueError:
            msg = 'S4 must be a float between 0 and 1.'
            error_messages.append(msg)

        GL = self.gen_limit.get().strip()
        if GL == '':
            GL = 0
        else:
            try:
                GL = int(GL)
                if GL <= 0:
                    raise ValueError
            except ValueError:
                msg = 'Generation limit must be a positive integer (or empty).'
                error_messages.append(msg)

        if len(error_messages) == 0:
            return P, L, S1, S2, S3, S4, GL
        messagebox.showerror('Input Error', '\n'.join(error_messages))
        return None

    def run_btn_action(self):
        """
        Defines the action to be taken when user clicks the "Start"/"Resume"
        button. Note that those are the same button with changing label.
        :return: None.
        """
        if self.cellular_automaton.state.is_stopped:
            params = self.get_input()
            if params:
                P, L, S1, S2, S3, S4, GL = params
                self.run_btn.place_forget()
                self.cellular_automaton.set(P, L, S1, S2, S3, S4, GL)
                self.cellular_automaton.run()
        elif self.cellular_automaton.state.is_paused:
            self.run_btn.place_forget()
            self.cellular_automaton.run()

    def pause_btn_action(self):
        """
        Defines the action to be taken when user clicks the "Pause" button.
        :return: None.
        """
        self.run_btn.place(relx=0.01, rely=0.745, width=265, height=40)
        self.run_btn.configure(text='\u23F5 Resume  ', font=fonts.bold)
        self.cellular_automaton.pause()

    def stop_btn_action(self):
        """
        Defines the action to be taken when user click the "Stop" button.
        :return: None.
        """
        self.run_btn.place(relx=0.01, rely=0.745, width=265, height=40)
        self.run_btn.configure(text='\u23F5 Start   ', font=fonts.bold)
        self.cellular_automaton.stop()