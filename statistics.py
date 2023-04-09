import threading
import tkinter as tk
from multiprocessing.pool import RUN

from app import App


def run_app(app):
    app.run_btn_action()


def automatic_iterations(app, num_iterations):
    for i in range(num_iterations):
        run_app(app)
        app.update()
        app.after(3000)  # wait for 2 seconds before next iteration


if __name__ == '__main__':
    app = App()
    app.isTest = True
    app.iterations = 9


    def run():
        t = threading.Thread(target=start_iterations)
        t.start()


    def start_iterations():
        # Disable the start button to prevent multiple runs at once
        start_button.config(state=tk.DISABLED)

        # Run the app manually
        run_app(app)
        app.update()

        # Start the automatic iterations after 2 seconds
        app.after(1000, automatic_iterations, app, app.iterations)


    # Create a button to start the iterations
    start_button = tk.Button(app, text="Run statistics", command=start_iterations)
    start_button.pack()

    app.mainloop()
