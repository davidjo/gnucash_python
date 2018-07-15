

#include <gtk/gtk.h>

#include <stdio.h>

main(int argc, char **argv)
{
	fprintf(stdout,"sizeof GtkBin is %d %x\n",sizeof(GtkBin),sizeof(GtkBin));
	fprintf(stdout,"sizeof GtkContainer is %d %x\n",sizeof(GtkContainer),sizeof(GtkContainer));
	fprintf(stdout,"sizeof GtkWidget is %d %x\n",sizeof(GtkWidget),sizeof(GtkWidget));

	//fprintf(stdout,"offset GtkContainer  has_focus_chain is %d %x\n",offsetof(GtkContainer,has_focus_chain),offsetof(GtkContainer,has_focus_chain));
	fprintf(stdout,"offset GtkContainer  focus_child is %d %x\n",offsetof(GtkContainer,focus_child),offsetof(GtkContainer,focus_child));
	fprintf(stdout,"offset GtkBin  child %d %x\n",offsetof(GtkBin,child),offsetof(GtkBin,child));
}
