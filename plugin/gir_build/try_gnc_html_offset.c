

#include <gtk/gtk.h>

#include <stdio.h>


struct _GncHtmlPrivate
{
	int jnk;
};

typedef struct _GncHtmlPrivate GncHtmlPrivate;

struct _GncHtml
{
    GtkBin parent_instance;

    /*< private >*/
    GncHtmlPrivate* priv;
};

typedef struct _GncHtml GncHtml;


int main(int argc, char **argv)
{
	fprintf(stdout,"sizeof GtkBin is %lu %lx\n",sizeof(GtkBin),sizeof(GtkBin));
	fprintf(stdout,"sizeof GtkContainer is %lu %lx\n",sizeof(GtkContainer),sizeof(GtkContainer));
	fprintf(stdout,"sizeof GtkWidget is %lu %lx\n",sizeof(GtkWidget),sizeof(GtkWidget));

	//fprintf(stdout,"offset GtkContainer  has_focus_chain is %d %x\n",offsetof(GtkContainer,has_focus_chain),offsetof(GtkContainer,has_focus_chain));
	//fprintf(stdout,"offset GtkContainer  focus_child is %d %x\n",offsetof(GtkContainer,focus_child),offsetof(GtkContainer,focus_child));
	//fprintf(stdout,"offset GtkBin  child %d %x\n",offsetof(GtkBin,child),offsetof(GtkBin,child));

	GncHtml try;

	fprintf(stdout,"offset GncHtml priv %lu %lx\n",offsetof(GncHtml,priv),offsetof(GncHtml,priv));
}
